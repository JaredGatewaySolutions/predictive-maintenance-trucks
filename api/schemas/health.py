"""
Health Check and Metrics Schemas
==================================
Pydantic models for health and monitoring endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class HealthResponse(BaseModel):
    """
    API health check response.
    """
    status: str = Field(..., description="Health status: healthy, degraded, unhealthy")
    timestamp: str = Field(..., description="Check timestamp (ISO 8601)")
    model_loaded: bool = Field(..., description="Whether model is loaded")
    model_version: Optional[str] = Field(None, description="Current model version")
    uptime_seconds: Optional[float] = Field(None, description="API uptime in seconds")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2025-11-15T17:50:00.123456",
                "model_loaded": True,
                "model_version": "v1_20251115_173242",
                "uptime_seconds": 3600.5
            }
        }


class MetricsResponse(BaseModel):
    """
    Model performance metrics and API statistics.
    """
    model_version: str = Field(..., description="Current model version")
    training_date: Optional[str] = Field(None, description="Model training date")
    metrics: Dict[str, Any] = Field(..., description="Model performance metrics")
    predictions_made: int = Field(..., description="Total predictions made since startup")
    uptime_seconds: float = Field(..., description="API uptime in seconds")
    
    class Config:
        schema_extra = {
            "example": {
                "model_version": "v1_20251115_173242",
                "training_date": "2025-11-15T17:32:42",
                "metrics": {
                    "accuracy": 0.900,
                    "auc_roc": 0.703,
                    "training_samples": 800,
                    "test_samples": 200,
                    "optimal_threshold": 0.10,
                    "cost_savings": 2388.0
                },
                "predictions_made": 127,
                "uptime_seconds": 3600.5
            }
        }
