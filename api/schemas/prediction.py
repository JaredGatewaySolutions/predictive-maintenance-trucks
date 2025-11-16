"""
Prediction Request/Response Schemas
====================================
Pydantic models for prediction endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class VehicleFeatures(BaseModel):
    """
    Vehicle sensor data and features.
    All 170 SCANIA features are optional to handle missing data.
    """
    # Allow any field name to handle all 170 features dynamically
    class Config:
        extra = "allow"  # Allow additional fields not explicitly defined
    
    # Document key features (examples)
    aa_000: Optional[float] = Field(None, description="Sensor reading aa_000")
    ab_000: Optional[float] = Field(None, description="Sensor reading ab_000")
    ac_000: Optional[float] = Field(None, description="Sensor reading ac_000")
    # ... 167 more features handled by extra="allow"


class SinglePredictionRequest(BaseModel):
    """
    Request for single vehicle prediction.
    """
    vehicle_id: Optional[str] = Field(None, description="Vehicle identifier")
    features: Dict[str, Any] = Field(..., description="Vehicle features (170 sensor readings)")
    
    class Config:
        schema_extra = {
            "example": {
                "vehicle_id": "V12345",
                "features": {
                    "aa_000": 76294,
                    "ab_000": 0,
                    "ac_000": 2130706432,
                    # ... more features
                }
            }
        }


class BatchPredictionRequest(BaseModel):
    """
    Request for batch predictions on multiple vehicles.
    """
    vehicles: List[SinglePredictionRequest] = Field(
        ..., 
        description="List of vehicles to predict"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "vehicles": [
                    {
                        "vehicle_id": "V12345",
                        "features": {"aa_000": 76294, "ab_000": 0}
                    },
                    {
                        "vehicle_id": "V12346",
                        "features": {"aa_000": 80000, "ab_000": 10}
                    }
                ]
            }
        }


class PredictionResponse(BaseModel):
    """
    Response for single prediction.
    """
    prediction_id: str = Field(..., description="Unique prediction identifier")
    vehicle_id: Optional[str] = Field(None, description="Vehicle identifier")
    prediction: int = Field(..., description="Prediction class (0=healthy, 1=failure)")
    probability: float = Field(..., description="Failure probability (0.0-1.0)")
    risk_level: str = Field(..., description="Risk level: HIGH, MEDIUM, or LOW")
    timestamp: str = Field(..., description="Prediction timestamp (ISO 8601)")
    model_version: str = Field(..., description="Model version used")
    
    class Config:
        schema_extra = {
            "example": {
                "prediction_id": "pred_20251115_175000_abc123",
                "vehicle_id": "V12345",
                "prediction": 1,
                "probability": 0.85,
                "risk_level": "HIGH",
                "timestamp": "2025-11-15T17:50:00.123456",
                "model_version": "v1_20251115_173242"
            }
        }


class BatchPredictionResponse(BaseModel):
    """
    Response for batch predictions.
    """
    predictions: List[PredictionResponse] = Field(..., description="List of predictions")
    total_count: int = Field(..., description="Total number of predictions")
    timestamp: str = Field(..., description="Batch processing timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "predictions": [
                    {
                        "prediction_id": "pred_20251115_175000_abc123",
                        "vehicle_id": "V12345",
                        "prediction": 1,
                        "probability": 0.85,
                        "risk_level": "HIGH",
                        "timestamp": "2025-11-15T17:50:00.123456",
                        "model_version": "v1_20251115_173242"
                    }
                ],
                "total_count": 1,
                "timestamp": "2025-11-15T17:50:00.123456"
            }
        }


class PredictionHistory(BaseModel):
    """
    Historical predictions for a vehicle.
    """
    vehicle_id: str = Field(..., description="Vehicle identifier")
    predictions: List[PredictionResponse] = Field(..., description="Past predictions")
    count: int = Field(..., description="Number of predictions")
    first_prediction: Optional[str] = Field(None, description="First prediction timestamp")
    last_prediction: Optional[str] = Field(None, description="Last prediction timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "vehicle_id": "V12345",
                "predictions": [
                    {
                        "prediction_id": "pred_20251115_175000_abc123",
                        "vehicle_id": "V12345",
                        "prediction": 1,
                        "probability": 0.85,
                        "risk_level": "HIGH",
                        "timestamp": "2025-11-15T17:50:00.123456",
                        "model_version": "v1_20251115_173242"
                    }
                ],
                "count": 1,
                "first_prediction": "2025-11-15T17:50:00.123456",
                "last_prediction": "2025-11-15T17:50:00.123456"
            }
        }
