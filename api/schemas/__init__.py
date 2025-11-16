"""
Pydantic Schemas for API Request/Response Validation
=====================================================
"""

from .prediction import (
    VehicleFeatures,
    SinglePredictionRequest,
    BatchPredictionRequest,
    PredictionResponse,
    BatchPredictionResponse
)
from .health import HealthResponse, MetricsResponse

__all__ = [
    "VehicleFeatures",
    "SinglePredictionRequest",
    "BatchPredictionRequest",
    "PredictionResponse",
    "BatchPredictionResponse",
    "HealthResponse",
    "MetricsResponse"
]
