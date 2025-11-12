import os
import time
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel, ConfigDict
from azure.storage.blob import BlobServiceClient  # 👈 added import to fetch model from Azure Blob

# -----------------------------
# Environment + Config
# -----------------------------
APP_VERSION = os.getenv("APP_VERSION", "0.1.0")
MODEL_DIR = "/model"                                 # where model will be stored inside container
MODEL_FILE = f"{MODEL_DIR}/pipeline.joblib"          # expected local model path
AZURE_CONN_STR = os.getenv("AZURE_STORAGE_CONNECTION_STRING")  # fetched from K8S secret
AZURE_CONTAINER = os.getenv("AZURE_MODEL_CONTAINER", "ml-models")  # can be overridden in env
AZURE_BLOB_NAME = os.getenv("AZURE_MODEL_BLOB", "pipeline.joblib")  # model filename in blob

# -----------------------------
# Utility: Download model if not exists
# -----------------------------
def download_model_from_blob():
    """Downloads the model artifact from Azure Blob Storage into /model."""
    if not AZURE_CONN_STR:
        raise RuntimeError("AZURE_STORAGE_CONNECTION_STRING not found in environment variables.")

    os.makedirs(MODEL_DIR, exist_ok=True)
    print(f"🔍 Checking Azure Blob for model: container={AZURE_CONTAINER}, blob={AZURE_BLOB_NAME}")

    blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONN_STR)
    blob_client = blob_service_client.get_blob_client(container=AZURE_CONTAINER, blob=AZURE_BLOB_NAME)

    # Download model bytes to local /model directory
    with open(MODEL_FILE, "wb") as f:
        f.write(blob_client.download_blob().readall())

    print(f"✅ Model downloaded successfully from Azure Blob to {MODEL_FILE}")

# -----------------------------
# FastAPI lifecycle: load model on startup
# -----------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifecycle context: runs on startup and shutdown."""
    global _model, _expected_features, _supports_proba, _allowed_type_categories

    # Step 1 — Download model if missing
    if not os.path.exists(MODEL_FILE):
        print("📦 Local model not found — downloading from Azure Blob...")
        download_model_from_blob()
    else:
        print("📁 Local model already present, skipping download...")

    # Step 2 — Load model into memory
    _model = joblib.load(MODEL_FILE)
    _expected_features = _get_expected_features(_model)
    _supports_proba = hasattr(_model, "predict_proba")
    _allowed_type_categories = getattr(_model, "type_categories_", None)
    print("✅ Model loaded successfully and ready for inference.")
    yield


# -----------------------------
# App setup
# -----------------------------
app = FastAPI(
    title="Fraud Detection Inference API",
    version=APP_VERSION,
    description="Serves fraud predictions from a trained fraud-detection pipeline.",
    lifespan=lifespan,
)

# Prometheus metrics instrumentation
Instrumentator().instrument(app).expose(app)

# -----------------------------
# Request/Response Models
# -----------------------------
class PredictRequest(BaseModel):
    records: List[Dict[str, Any]]

class PredictResponse(BaseModel):
    predictions: List[int]
    probabilities: Optional[List[float]] = None
    model_version: Optional[str] = None
    inference_ms: float  # latency per call in milliseconds
    model_config = ConfigDict(protected_namespaces=())

# -----------------------------
# Global Model Cache
# -----------------------------
_model: Optional[Any] = None
_expected_features: Optional[List[str]] = None
_supports_proba: bool = False
_allowed_type_categories: Optional[list] = None

def _get_expected_features(m) -> Optional[List[str]]:
    """Extract expected feature names from model."""
    names = getattr(m, "feature_names_in_", None)
    if names is None:
        names = getattr(m, "raw_feature_names_in_", None)
    return list(names) if names is not None else None


# -----------------------------
# Health + Readiness Probes
# -----------------------------
@app.get("/healthcheck")
def healthcheck():
    """Kubernetes health probe."""
    return {
        "status": "ok",
        "model_loaded": _model is not None,
        "version": APP_VERSION,
        "expected_features": _expected_features,
    }

@app.get("/ready")
def ready():
    """Readiness probe for AKS."""
    if _model is None:
        raise HTTPException(status_code=503, detail="Model not loaded yet")
    return {"status": "ready", "version": APP_VERSION}


# -----------------------------
# Prediction Endpoint
# -----------------------------
@app.post("/predict", response_model=PredictResponse, response_model_exclude_none=True)
def predict(
    req: PredictRequest,
    return_proba: bool = Query(True, description="Include class-1 probabilities if supported"),
):
    """Main inference endpoint."""
    if _model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    if not req.records:
        raise HTTPException(status_code=422, detail="`records` must be a non-empty list")

    t0 = time.perf_counter()
    df = pd.DataFrame(req.records)

    # --- validate input features ---
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

    # --- perform prediction ---
    try:
        preds = _model.predict(df).tolist()
        proba = _model.predict_proba(df)[:, -1].tolist() if (return_proba and _supports_proba) else None
        elapsed_ms = (time.perf_counter() - t0) * 1000

        return PredictResponse(
            predictions=preds,
            probabilities=proba,
            model_version=APP_VERSION,
            inference_ms=elapsed_ms,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Inference error: {e}")
