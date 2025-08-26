# ML/dtypes.py
import pandas as pd

def cast_fn(df, cats=None, num_cols=None, all_cols=None, categorical_col="type"):
    df = pd.DataFrame(df).copy()

    # keep only known columns (optional safety)
    if all_cols is not None:
        df = df[[c for c in df.columns if c in all_cols]]

    # cast categorical
    if categorical_col in df.columns:
        if cats is not None:
            df[categorical_col] = pd.Categorical(df[categorical_col], categories=cats, ordered=False)
            # strict: fail on unseen categories
            if df[categorical_col].isna().any():
                unseen = sorted(set(df[categorical_col].astype(str).unique()) - set(cats))
                if unseen:
                    raise ValueError(f"Unknown category in '{categorical_col}': {unseen}. Allowed: {cats}")
        else:
            df[categorical_col] = df[categorical_col].astype("category")

    # coerce numerics
    if num_cols:
        df[num_cols] = df[num_cols].apply(pd.to_numeric, errors="raise")

    # stable order
    if all_cols is not None:
        present = [c for c in all_cols if c in df.columns]
        df = df[present]
    return df
