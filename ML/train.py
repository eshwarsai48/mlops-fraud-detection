import os
import gc
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
import joblib

# ──────────────────────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────────────────────
MODEL_TYPE = os.environ.get("MODEL_TYPE", "xgb").lower()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "paysim.csv")
MODEL_DIR = os.path.join(BASE_DIR, "model")
ARTIFACT = os.path.join(MODEL_DIR, "pipeline.joblib")
os.makedirs(MODEL_DIR, exist_ok=True)

RANDOM_SEED = 21
# ──────────────────────────────────────────────────────────────────────────────
# Helpers: memory‑efficient feature builder
# ──────────────────────────────────────────────────────────────────────────────
def build_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds per-user time-based features using PaySim's 'step' (hours).
    Designed to be memory-efficient:
      * uses float32/int16/int8 where possible
      * avoids per-group DataFrame copies
      * uses groupby + rolling(on=...) instead of set_index in a loop
    """
    # Keep only the columns we need (already done at read_csv), set dtypes
    df = df.copy()

    # Precompute a proper time column from 'step' (hours)
    df["tx_time"] = pd.to_timedelta(df["step"].astype("int32"), unit="h")

    # Sort once (stable, in-place to avoid extra copies)
    df.sort_values(["nameOrig", "tx_time"], kind="mergesort", inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Per-user rolling windows using the time column
    # NOTE: groupby(...).rolling(window='2h', on='tx_time') returns a Series with a MultiIndex.
    # We immediately "reset" the group level by dropping it with reset_index(drop=True).
    grp = df.groupby("nameOrig", sort=False)

    # Counts
    df["tx_count_2h"] = (
        grp.rolling("2h", on="tx_time")["amount"].count()
           .reset_index(drop=True)
           .astype("int16")
    )
    df["tx_count_6h"] = (
        grp.rolling("6h", on="tx_time")["amount"].count()
           .reset_index(drop=True)
           .astype("int16")
    )

    # Amount stats
    df["tx_max_amt_2h"] = (
        grp.rolling("2h", on="tx_time")["amount"].max()
           .reset_index(drop=True)
           .astype("float32")
    )
    df["tx_avg_amt_2h"] = (
        grp.rolling("2h", on="tx_time")["amount"].mean()
           .reset_index(drop=True)
           .astype("float32")
    )
    df["tx_sum_amt_6h"] = (
        grp.rolling("6h", on="tx_time")["amount"].sum()
           .reset_index(drop=True)
           .astype("float32")
    )

    # Recency feature: hours since last tx (per user)
    df["hours_since_last_tx"] = (
        grp["tx_time"].diff().dt.total_seconds().div(3600).fillna(-1).astype("float32")
    )

    # Account maturity features
    df["tx_count_so_far"] = grp.cumcount().astype("int32")
    df["is_returning_user"] = (df["tx_count_so_far"] > 0).astype("int8")

    # Log-transform amount (becomes float32)
    df["amount_log"] = np.log1p(df["amount"]).astype("float32")

    return df

# ──────────────────────────────────────────────────────────────────────────────
# Load data (memory‑aware)
# ──────────────────────────────────────────────────────────────────────────────
# Only read the columns we actually use. Downcast to smaller dtypes.
usecols = ["step", "nameOrig", "amount", "type", "isFraud"]
dtypes = {
    "step": "int32",
    "nameOrig": "category",   # categories are very memory efficient
    "amount": "float32",
    "type": "category",       # we'll keep as category for XGB; code it for RF
    "isFraud": "int8"
}
df = pd.read_csv(DATA_PATH, usecols=usecols, dtype=dtypes, memory_map=True, low_memory=True)

# Build features
df = build_temporal_features(df)

# Select model features
model_input_features = [
    "type",                # categorical
    "amount",              # float32
    "amount_log",          # float32
    "tx_count_2h",         # int16
    "tx_count_6h",         # int16
    "tx_avg_amt_2h",       # float32
    "tx_sum_amt_6h",       # float32
    "tx_max_amt_2h",       # float32
    "hours_since_last_tx", # float32
    "tx_count_so_far",     # int32
    "is_returning_user"    # int8
]

X = df[model_input_features]
y = df["isFraud"].astype("int8")

# Free memory: drop columns we won't use further
drop_these = [c for c in df.columns if c not in model_input_features + ["isFraud"]]
df.drop(columns=drop_these, inplace=True, errors="ignore")
gc.collect()

# Train/val/test split (fixed bug: split temp into val/test, not X,y again)
X_train, X_temp, y_train, y_temp = train_test_split(
    X, y, test_size=0.30, stratify=y, random_state=RANDOM_SEED
)
X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp, test_size=0.50, stratify=y_temp, random_state=RANDOM_SEED
)
# ──────────────────────────────────────────────────────────────────────────────
# Build Pipeline
# ──────────────────────────────────────────────────────────────────────────────

# Handle categorical depending on model choice
use_xgb = MODEL_TYPE == "xgb"
if use_xgb:
    import xgboost as xgb  # fixed import name
    # Preprocessing: passthrough (keep DataFrame with 'type' as category).
    preprocessor = "passthrough" # whole preprocessor is "passthrough" so XGBoost sees the original columns (including the categorical type) exactly as trained.

    # Imbalance handling in a memory-friendly way
    pos = max(1, int(y_train.sum()))  # fraud transactions
    neg = int((y_train == 0).sum())  # non-fraud transactions
    scale_pos_weight = neg / pos  # tell XGBoost to weigh up-weight fraud samples, so they get equal attention

    print(f"[INFO] Training XGBoost (enable_categorical=True). XGBoost version: {xgb.__version__}")
    model = xgb.XGBClassifier(
        enable_categorical=True,
        tree_method="hist",  # fast & memory efficient
        max_depth=6,
        max_bin=256,  # tighter bins reduce memory
        n_estimators=300,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=RANDOM_SEED,
        n_jobs=-1,
        scale_pos_weight=scale_pos_weight,
        eval_metric=["auc", "logloss", ],
        early_stopping_rounds=50,
    )
    pipe = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("model", model),
    ])
else:
    # RandomForest with One-Hot on 'type'
    from sklearn.ensemble import RandomForestClassifier

    cat_features = ["type"]
    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_features),
        ],
        remainder="passthrough",  # pass other numeric features unchanged
        verbose_feature_names_out=False,
    )

    print("[INFO] Training RandomForest (OHE on 'type').")
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=18,
        max_features="sqrt",
        bootstrap=True,
        max_samples=0.8,
        n_jobs=-1,
        class_weight="balanced_subsample",
        random_state=RANDOM_SEED,
    )
    pipe = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("model", model),
    ])

#pipe.feature_names_in_ = np.asarray(X_train.columns, dtype=object) #turns the Pandas Index of your PaySim feature columns into a plain, 1-D NumPy array of strings to be used in FAST API
#removing the manual assignment
# ──────────────────────────────────────────────────────────────────────────────
# Fit
# ──────────────────────────────────────────────────────────────────────────────
fit_kwargs = {}
if use_xgb:
    # Pass validation to XGB through the pipeline
    fit_kwargs["model__eval_set"] = [(X_val, y_val)]
    fit_kwargs["model__verbose"] = True

pipe.fit(X_train, y_train, **fit_kwargs)
expected = getattr(pipe, "feature_names_in_", None)
if expected is None:
    expected = np.asarray(X_train.columns, dtype=object)
    setattr(pipe, "raw_feature_names_in_", expected)   # cleaner than pipe.__dict__[...]=...

print("Expected input columns for serving:", list(expected))



# ──────────────────────────────────────────────────────────────────────────────
# Evaluate
# ──────────────────────────────────────────────────────────────────────────────
y_pred = pipe.predict(X_test)

try:
    y_proba = pipe.predict_proba(X_test)[:, -1]
    auc = roc_auc_score(y_test, y_proba)
except Exception:
    y_proba, auc = None, None

print("\n=== Classification Report ===")
print(classification_report(y_test, y_pred, digits=4))
if auc is not None:
    print(f"AUC: {auc:.4f}")

# ──────────────────────────────────────────────────────────────────────────────
# Save model
# ──────────────────────────────────────────────────────────────────────────────
joblib.dump(pipe, ARTIFACT)
print(f"[OK] Saved pipeline → {ARTIFACT}")
print("Expected input columns for serving:", list(expected))
