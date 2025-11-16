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
    Vehicle sensor data - OPTIMAL 20 FEATURES ONLY.
    Selected via XGBoost Feature Importance Analysis (Nov 15, 2025).
    These 20 features achieve 92.3% recall and capture 28.6% of model importance.
    
    Feature format can be either:
    - Scania codes (158_9, 167_6, etc.) - preferred for API
    - M1 Abrams names (POWER_SYSTEM_METRIC_9, etc.) - converted automatically
    """
    
    # System Diagnostics & Performance (Highest Priority - Rank 1, 4, 18)
    field_158_9: Optional[float] = Field(None, alias="158_9", description="Power System Metric 9 (MOST IMPORTANT - 3.41%)")
    field_158_5: Optional[float] = Field(None, alias="158_5", description="Power System Metric 5 (1.71%)")
    field_158_6: Optional[float] = Field(None, alias="158_6", description="Power System Metric 6 (1.17%)")
    
    # Temperature & Environmental (Rank 2, 3, 9)
    field_167_6: Optional[float] = Field(None, alias="167_6", description="Moderate Temperature Operations (1.88%)")
    field_167_3: Optional[float] = Field(None, alias="167_3", description="Cold Weather Operations (1.77%)")
    field_167_1: Optional[float] = Field(None, alias="167_1", description="Low Temperature Operations (1.26%)")
    
    # Terrain & Mobility (Rank 5, 13, 15)
    field_291_4: Optional[float] = Field(None, alias="291_4", description="Terrain Type 4 (1.48%)")
    field_291_1: Optional[float] = Field(None, alias="291_1", description="Terrain Type 1 (1.22%)")
    field_291_5: Optional[float] = Field(None, alias="291_5", description="Terrain Type 5 (1.21%)")
    
    # Operational Stress (Rank 6, 7, 8, 10, 17, 20)
    field_459_3: Optional[float] = Field(None, alias="459_3", description="Operational Stress 3 (1.34%)")
    field_459_15: Optional[float] = Field(None, alias="459_15", description="Operational Stress 15 (1.29%)")
    field_459_8: Optional[float] = Field(None, alias="459_8", description="Operational Stress 8 (1.27%)")
    field_459_14: Optional[float] = Field(None, alias="459_14", description="Operational Stress 14 (1.26%)")
    field_459_9: Optional[float] = Field(None, alias="459_9", description="Operational Stress 9 (1.17%)")
    field_459_1: Optional[float] = Field(None, alias="459_1", description="Operational Stress 1 (1.28%)")
    
    # Load Distribution (Rank 11, 16, 20)
    field_272_0: Optional[float] = Field(None, alias="272_0", description="Load Distribution 0 (1.25%)")
    field_272_2: Optional[float] = Field(None, alias="272_2", description="Load Distribution 2 (1.18%)")
    field_272_4: Optional[float] = Field(None, alias="272_4", description="Load Distribution 4 (1.12%)")
    
    # Component Wear (Rank 12, 14, 19)
    field_397_33: Optional[float] = Field(None, alias="397_33", description="Component Wear 33 (1.23%)")
    field_397_0: Optional[float] = Field(None, alias="397_0", description="Component Wear 0 (1.22%)")
    field_397_3: Optional[float] = Field(None, alias="397_3", description="Component Wear 3 (1.15%)")
    
    class Config:
        allow_population_by_field_name = True  # Allow both field name and alias
        extra = "forbid"  # Reject extra fields - we only want these 20!


class SinglePredictionRequest(BaseModel):
    """
    Request for single vehicle prediction.
    """
    vehicle_id: Optional[str] = Field(None, description="Vehicle identifier")
    features: Dict[str, Any] = Field(..., description="Vehicle features (170 sensor readings)")
    
    class Config:
        schema_extra = {
            "example": {
                "vehicle_id": "TANK001",
                "features": {
                    "158_9": 1250.5,  # Power System (Most Important!)
                    "167_6": 850.2,   # Temperature - Moderate
                    "167_3": 420.1,   # Temperature - Cold
                    "158_5": 980.3,   # Power System
                    "291_4": 650.0,   # Terrain Type
                    "459_3": 340.7,   # Operational Stress
                    "459_15": 220.4,  # Operational Stress
                    "459_8": 180.5,   # Operational Stress
                    "167_1": 310.2,   # Temperature - Low
                    "459_14": 150.3,  # Operational Stress
                    "272_0": 500.1,   # Load Distribution
                    "397_33": 45.8,   # Component Wear
                    "291_1": 890.4,   # Terrain Type
                    "397_0": 120.5,   # Component Wear
                    "291_5": 430.2,   # Terrain Type
                    "272_2": 380.6,   # Load Distribution
                    "459_9": 95.3,    # Operational Stress
                    "158_6": 710.8,   # Power System
                    "397_3": 68.4,    # Component Wear
                    "272_4": 290.7    # Load Distribution
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
    fleet_name: Optional[str] = Field(None, description="Optional fleet name for grouping")
    
    class Config:
        schema_extra = {
            "example": {
                "vehicles": [
                    {
                        "vehicle_id": "TANK001",
                        "features": {
                            "158_9": 1250.5, "167_6": 850.2, "167_3": 420.1, "158_5": 980.3,
                            "291_4": 650.0, "459_3": 340.7, "459_15": 220.4, "459_8": 180.5,
                            "167_1": 310.2, "459_14": 150.3, "272_0": 500.1, "397_33": 45.8,
                            "291_1": 890.4, "397_0": 120.5, "291_5": 430.2, "272_2": 380.6,
                            "459_9": 95.3, "158_6": 710.8, "397_3": 68.4, "272_4": 290.7
                        }
                    },
                    {
                        "vehicle_id": "TANK002",
                        "features": {
                            "158_9": 1380.2, "167_6": 920.5, "167_3": 450.8, "158_5": 1050.1,
                            "291_4": 710.3, "459_3": 390.2, "459_15": 250.1, "459_8": 200.3,
                            "167_1": 340.5, "459_14": 170.2, "272_0": 550.4, "397_33": 52.1,
                            "291_1": 950.2, "397_0": 135.3, "291_5": 470.8, "272_2": 410.2,
                            "459_9": 105.1, "158_6": 780.3, "397_3": 75.2, "272_4": 320.5
                        }
                    }
                ],
                "fleet_name": "Alpha Fleet"
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
