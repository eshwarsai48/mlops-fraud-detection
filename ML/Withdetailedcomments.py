import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score

# --- Choose your model here: "xgb" or "rf" ---
MODEL_TYPE = os.environ.get("MODEL_TYPE", "xgb")  # or "rf"

# ---- Paths ----
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "paysim.csv")
MODEL_DIR = os.path.join(BASE_DIR, "model")
os.makedirs(MODEL_DIR, exist_ok=True)

# -------------------------------------------------
# Feature engineering: true time-based windows per user
# -------------------------------------------------
def build_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds per-user time-based features using PaySim's 'step' (hours).
    Returns a new DataFrame with extra columns; original columns preserved.
    """
    df = df.copy()

    # 1) Make a time index from 'step' (hours since start)
    df['tx_time'] = pd.to_timedelta(df['step'], unit='h')

    # 2) Sort per user & time
    df.sort_values(['nameOrig', 'tx_time'], inplace=True)

    # 3) Apply per-user rolling windows & gaps
    def _per_user(g: pd.DataFrame) -> pd.DataFrame:#(_per_user->_ is used before the name in internal functions mentioning per user is only to be used by temporal function)
        g = g.set_index('tx_time')

        # Frequency in last 6h/24h
        g['tx_count_6h']  = g['amount'].rolling('6H',  min_periods=1).count()
        g['tx_count_24h'] = g['amount'].rolling('24H', min_periods=1).count()

        # Amount stats in windows
        g['tx_avg_amt_6h']  = g['amount'].rolling('6H',  min_periods=1).mean()
        g['tx_sum_amt_24h'] = g['amount'].rolling('24H', min_periods=1).sum()
        g['tx_max_amt_6h']  = g['amount'].rolling('6H',  min_periods=1).max()

        # Time since last transaction (hours)
        g['hours_since_last_tx'] = g.index.to_series().diff().dt.total_seconds().div(3600) #checks the difference between timestamps for the last transaction and the current
        #.to_series() just turns that index into a pandas Series so we can use Series operations like .diff(). and we divide by 3600 s to convert into hours
        g['hours_since_last_tx'] = g['hours_since_last_tx'].fillna(-1)  # first tx has (-1) to avoid NA

        # Running count & new/returning
        g['tx_count_so_far']   = np.arange(len(g)) # counts how many transactions did the user make
        g['is_returning_user'] = (g['tx_count_so_far'] > 0).astype(int) # is returning user or not

        return g.reset_index() #Moves tx_time from the index back into a normal column.

    out = (
        df.groupby('nameOrig', group_keys=False) #here df.groupby nameorig would split the data frame into chunks to be passed into the _peruser function, group_keys is set to false because we want the user name to be displayed each row and not once and all the grouping happening under it
          .apply(_per_user) # stitches the outputs into one big DF
          .sort_values(['nameOrig', 'tx_time']) #sort the values
          .reset_index(drop=True) #resets the index, because for every user a new index is created from 0,1,2 and we do not want multiple indexes having 0,1,2 e.t.c
    ) #Ascending order = chronological flow (better for feature consistency & debugging).
#Descending order = last transactions first (better for snapshot-style scoring).

    # amount_log helps with skew; safe & model-friendly
    out['amount_log'] = np.log1p(out['amount'])

    return out

# -------------------------------------------------
# Load & prepare data
# -------------------------------------------------
df = pd.read_csv(DATA_PATH) ##usual naming convention, the read happens after the function is defined

# (Optional) work on a sample during dev to keep it fast
if int(os.environ.get("SAMPLE_N", "0")) > 0:
    n = int(os.environ["SAMPLE_N"])
    df = df.sample(n=n, random_state=42)

df_feats = build_temporal_features(df)

# -------------------------------------------------
# Choose features (Leakage note):
# Avoid using newbalance*/oldbalance* by default.
# Uncomment at your own risk after you understand leakage implications.
# -------------------------------------------------
base_features = [
    'type',               # categorical
    'amount',             # numeric (raw)
    'amount_log',         # numeric (log-transformed)
    'tx_count_6h',        # frequency (6h)
    'tx_count_24h',       # frequency (24h)
    'tx_avg_amt_6h',      # amount behavior (6h)
    'tx_sum_amt_24h',     # amount behavior (24h)
    'tx_max_amt_6h',      # burstiness (6h)
    'hours_since_last_tx',# recency
    'tx_count_so_far',    # account maturity
    'is_returning_user'   # new vs returning
]

# If you REALLY want balances, add here (understand possible leakage first):
# base_features += ['oldbalanceOrg','newbalanceOrig','oldbalanceDest','newbalanceDest']

X = df_feats[base_features].copy() # copy is a safety measure so your model training data is insulated from accidental modifications to the master dataset.
y = df_feats['isFraud'].astype(int) #hygiene, we are making sure its an integer, not a bool or float type

# -------------------------------------------------
# Handle categorical depending on model choice
# -------------------------------------------------
if MODEL_TYPE.lower() == "xgb": #lower is specified here because even if user types XGB/xGB, it will convert to lower, prevent it from taking the wrong branch
    # Native categorical handling (XGBoost >= 1.3)
    # Keep 'type' as pandas 'category', do NOT convert to codes
    X['type'] = X['type'].astype('category')
    use_xgb = True
else:
    # RandomForest in scikit-learn expects numerics -> label encode 'type'
    use_xgb = False
    # Map each category to an int deterministically
    X['type'] = X['type'].astype('category').cat.codes #cat.codes (ordinal encoding or integer encoding)

# -------------------------------------------------
# Train/test split (stratify because fraud is rare)
# -------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
) #stratify=y ensures that train, validation, and test all have the same class balance as the original dataset, which is crucial for imbalanced problems like fraud detection.
#for example if the orginal data set has 3% fraud cases, we want the test and validated data to have 3 % as well so there is no issue while training the data


# -------------------------------------------------
# Train model
# -------------------------------------------------
if use_xgb:
    import xgboost as xgb
    print(f"[INFO] Training XGBoost (enable_categorical=True). XGBoost version: {xgb.__version__}")
    model = xgb.XGBClassifier(
        enable_categorical=True, # Use pandas category columns directly (XGBoost ≥ 1.3). Avoids manual encoding.
        tree_method="hist",   # fast & memory efficient
        max_depth=6, #prevents overfitting
        n_estimators=300, # Upper bound on number of boosting rounds
        learning_rate=0.1, #Shrinks each tree’s contribution; lower rates (e.g., 0.05) often need more trees but can generalize better
        subsample=0.8, # Use 80% of rows per tree → adds stochasticity, helps prevent overfitting.
        colsample_bytree=0.8, # Use 80% of features per tree → more randomness, better generalization.
        random_state=42,
        eval_metric="logloss","auc" #Tracks log loss during training. For fraud, you might also add "auc" to monitor ranking performance.
        # AUC stands for Area Under the Curve, and in the fraud-detection context we almost always mean AUC-ROC:
        #check notes on AUC/ROC
        n_jobs=-1 # Use all available CPU cores.
    )
    model.fit(X_train, y_train, eval_set=[(X_val, y_val)], eval_metric=["logloss", "auc"], early_stopping_rounds=50, verbose=True) #Verbose= true gives the output of iteration compared to the validation data, helps us understand early stopping rounds, if a model stops improving, we would know why
    evals_result = model.evals_result()
    print(f"[XGB] Best iteration: {model.best_iteration}") #model.best_iteration and model.best_score are internal functions
    print(f"[XGB] Best AUC (val): {model.best_score:.6f}") # The "[XGB]" part is just a label you typed inside the f‑string so logs are easy to scan. It’s not fetched from anywhere.
else:
    from sklearn.ensemble import RandomForestClassifier
    print("[INFO] Training RandomForest (label-encoded 'type').")
    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=None,
        n_jobs=-1,
        class_weight="balanced_subsample", #used in cases like fraud datasets, where the dataset is imbalanced, fraud happens rarley, prevents the model from tilting towards the majority
        random_state=42
    )
    model.fit(X_train, y_train)

# -------------------------------------------------
# Evaluate
# -------------------------------------------------
y_pred = model.predict(X_test)
try:
    y_proba = model.predict_proba(X_test)[:, 1] # predict_proba() → returns probabilities for each class in a shape (n_samples, n_classes).
    #Column 0 = probability of class 0 (non-fraud)
    #Column 1 = probability of class 1 (fraud)
    #[:, 1] → takes just the probability of fraud (class 1).
    #These are soft predictions — e.g., 0.92 means "92% confident it's fraud".
    auc = roc_auc_score(y_test, y_proba) # roc_auc_score() → measures the model's ability to rank frauds above non-frauds at all thresholds, not just 0.5.
    #Needs probabilities (y_proba), not just class labels.
except Exception:
    y_proba = None
    auc = None

print("\n=== Classification Report ===")
print(classification_report(y_test, y_pred, digits=4))
if auc is not None:
    print(f"AUC: {auc:.4f}")

# -------------------------------------------------
# Save model
# -------------------------------------------------
out_path = os.path.join(MODEL_DIR, f"paysim_{'xgb' if use_xgb else 'rf'}.pkl")
try:
    # xgboost uses its own save; sklearn uses joblib
    if use_xgb:
        model.save_model(out_path.replace(".pkl", ".json"))  # portable json
        print(f"[OK] Saved XGBoost model → {out_path.replace('.pkl', '.json')}")
    else:
        import joblib
        joblib.dump(model, out_path)
        print(f"[OK] Saved RandomForest model → {out_path}")
except Exception as e:
    print(f"[WARN] Could not save model: {e}")
