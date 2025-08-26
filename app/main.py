import os
import time
from typing import Any, Dict, List, Optional

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, Any

APP_VERSION = os.getenv("APP_VERSION", "0.1.0")
MODEL_ARTIFACT = os.getenv("MODEL_ARTIFACT", "model/pipeline.joblib")

app = FastAPI(
    title="Fraud Detection Inference API",
    version=APP_VERSION,
    description="Serves fraud predictions from a trained pipeline."
)
#----Request/Response----
class PredictRequest(BaseModel):
    records: List[Dict[str, Any]]

class PredictResponse(BaseModel):
    predictions: List[int]
    probabilities: Optional[List[float]] = None
    model_version: Optional[str] = None
    inference_ms: float #latency for the call in ms

# ---Module level cache at start up----
_model: Optional[Any]= None
_expected_features: Optional[List[str]] = None
_supports_proba: bool= False
_allowed_type_categories: Optional[list] = None

def _get_expected_features(m) -> Optional[List[str]]:
    names = getattr(m, "feature_names_in_", None)
    if names is None:
        names = getattr(m, "raw_feature_names_in_", None)
    return list(names) if names is not None else None

#-------Run on Start Up-------
@app.on_event("startup")
def startup():
    global _model,_expected_features,_supports_proba, _allowed_type_categories
    if not os.path.exists(MODEL_ARTIFACT):
        raise RuntimeError(f"Model {MODEL_ARTIFACT} not found")
    _model = joblib.load(MODEL_ARTIFACT)
    _expected_features = _get_expected_features(_model)
    _supports_proba = hasattr(_model, "predict_proba")
    _allowed_type_categories = getattr(_model, "type_categories_", None)

#------Health checks--------
@app.get("/healthcheck")
def healthcheck():
    return {
        "status": "ok",
        "model_loaded": _model is not None,
        "version": APP_VERSION,
        "expected_features": _expected_features
    }
    if _allowed_type_categories is not None:
        body["allowed_type_categories"] = _allowed_type_categories
    return body
@app.get("/ready")
def ready():
    if _model is None:
        raise HTTPException(status_code=503, detail="Model not found")
    return {"status": "ready", "version": APP_VERSION}

#---Prediction Endpoint---
@app.post("/predict", response_model=PredictResponse,response_model_exclude_none=True) #Any fields whose value is None are omitted from the final JSON.
def predict(
    req: PredictRequest,
    return_proba: bool = Query(True, description="Include class-1 probabilities if supported"),
):
    if _model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    if not req.records:
        raise HTTPException(status_code=422, detail="`records` must be a non-empty list")

    t0 = time.perf_counter()
    df = pd.DataFrame(req.records)

    if _expected_features:
        missing = [c for c in _expected_features if c not in df.columns]
        if missing:
            raise HTTPException(
                status_code=422,
                detail={
                    "message": "Missing required features",
                    "missing_features": missing,
                    "expected_features": _expected_features,
                    "received_columns": list(df.columns),
                },
            )
        extras = [c for c in df.columns if c not in _expected_features]
        if extras:
            df = df.drop(columns=extras)
        df = df[_expected_features]

    #---#Predict the data---

    try:
        preds = _model.predict(df)
        proba = _model.predict_proba(df)[:,-1].tolist() if (return_proba and _supports_proba) else None
        elapsed_ms = (time.perf_counter() - t0) * 1000
        return PredictResponse(
            predictions=preds,
            probabilities=proba,  # will be a list or None
            model_version=APP_VERSION,
            inference_ms=elapsed_ms,
    )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Inference error: {e}")












