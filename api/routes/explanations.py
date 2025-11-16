"""
Explanation Endpoints
=====================
API endpoints for SHAP-based explanations of predictions.

Endpoints:
- GET /api/v1/explain/{vehicle_id} - Generate SHAP explanation for a vehicle
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import pandas as pd
import json
from pathlib import Path
from core.feature_mapper import SCANIA_TO_ABRAMS, FEATURE_DESCRIPTIONS

router = APIRouter(prefix="/api/v1", tags=["explanations"])

# Directory for storing predictions
PREDICTIONS_DIR = Path("data/predictions")


class ExplanationFactor(BaseModel):
    """Individual risk factor from SHAP analysis."""
    feature: str = Field(..., description="Feature name")
    description: Optional[str] = Field(None, description="Human-readable feature description")
    value: float = Field(..., description="Feature value for this vehicle")
    shap_value: float = Field(..., description="SHAP value (contribution to prediction)")
    effect: str = Field(..., description="INCREASES or DECREASES risk")


class ExplanationResponse(BaseModel):
    """Response with SHAP explanation for a vehicle prediction."""
    vehicle_id: str = Field(..., description="Vehicle identifier")
    prediction_id: Optional[str] = Field(None, description="Associated prediction ID")
    prediction_proba: float = Field(..., description="Failure probability")
    risk_level: str = Field(..., description="Risk level: HIGH, MEDIUM, LOW")
    top_factors: List[ExplanationFactor] = Field(..., description="Top contributing factors")
    explanation_text: str = Field(..., description="Human-readable explanation")
    timestamp: str = Field(..., description="Explanation timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "vehicle_id": "V12345",
                "prediction_id": "pred_20251115_175000_abc123",
                "prediction_proba": 0.85,
                "risk_level": "HIGH",
                "top_factors": [
                    {
                        "feature": "ENGINE_HOURS",
                        "description": "Turbine operating time - Primary service life limiter per DoD specs",
                        "value": 2450.0,
                        "shap_value": 0.123,
                        "effect": "INCREASES"
                    },
                    {
                        "feature": "TEMP_MODERATE_MI",
                        "description": "Miles operated in moderate temperature conditions",
                        "value": 1200.0,
                        "shap_value": -0.045,
                        "effect": "DECREASES"
                    }
                ],
                "explanation_text": "Primary risk driver: ENGINE_HOURS (contributes +0.123 to failure risk)",
                "timestamp": "2025-11-15T17:50:00.123456"
            }
        }


@router.get("/explain/{vehicle_id}", response_model=ExplanationResponse)
async def explain_prediction(vehicle_id: str, api_request: Request):
    """
    Generate SHAP explanation for a vehicle's prediction.
    
    This endpoint answers "WHY is this vehicle predicted to fail?"
    by showing the top features contributing to the prediction.
    
    Args:
        vehicle_id: Vehicle identifier
        api_request: FastAPI request object
    
    Returns:
        ExplanationResponse with SHAP values and human-readable explanation
    """
    try:
        # Get pipeline and analyzer from app state
        pipeline = api_request.app.state.pipeline
        analyzer = api_request.app.state.analyzer
        
        if pipeline is None or pipeline.predictor is None:
            raise HTTPException(
                status_code=503,
                detail="Model not loaded. Service unavailable."
            )
        
        if analyzer is None:
            raise HTTPException(
                status_code=503,
                detail="Explainability analyzer not initialized. SHAP explanations unavailable."
            )
        
        # Load vehicle prediction data
        file_path = PREDICTIONS_DIR / f"{vehicle_id}.json"
        
        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"No predictions found for vehicle {vehicle_id}. Run prediction first."
            )
        
        # Load prediction data
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        predictions_list = data.get("predictions", [])
        
        if not predictions_list:
            raise HTTPException(
                status_code=404,
                detail=f"No predictions found for vehicle {vehicle_id}"
            )
        
        # Get most recent prediction
        latest_prediction = predictions_list[-1]
        
        # Extract features
        features = latest_prediction.get("features")
        if not features:
            raise HTTPException(
                status_code=400,
                detail="Prediction does not contain feature data. Cannot generate explanation."
            )
        
        # Convert to pandas Series
        vehicle_series = pd.Series(features)
        
        # Generate SHAP explanation
        explanation = analyzer.explain_prediction(
            vehicle_series,
            instance_id=vehicle_id,
            top_n=10
        )
        
        if explanation is None:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate explanation. SHAP analysis error."
            )
        
        # Build response with top factors - translate Scania codes to Abrams names
        top_factors = []
        for factor in explanation["top_factors"]:
            # Get human-readable M1 Abrams feature name
            scania_code = factor["feature"]
            abrams_name = SCANIA_TO_ABRAMS.get(scania_code, scania_code)
            feature_description = FEATURE_DESCRIPTIONS.get(abrams_name, None)
            
            top_factors.append(ExplanationFactor(
                feature=abrams_name,
                description=feature_description,
                value=factor["value"],
                shap_value=factor["shap_value"],
                effect="INCREASES" if factor["shap_value"] > 0 else "DECREASES"
            ))
        
        # Create human-readable explanation with M1 Abrams feature names
        primary_factor = explanation["top_factors"][0]
        primary_factor_code = primary_factor['feature']
        primary_factor_name = SCANIA_TO_ABRAMS.get(primary_factor_code, primary_factor_code)
        
        if primary_factor["shap_value"] > 0:
            explanation_text = (
                f"Primary risk driver: {primary_factor_name} "
                f"(contributes +{primary_factor['shap_value']:.3f} to failure risk)"
            )
        else:
            explanation_text = (
                f"Primary protective factor: {primary_factor_name} "
                f"(reduces failure risk by {abs(primary_factor['shap_value']):.3f})"
            )
        
        # Build response
        response = ExplanationResponse(
            vehicle_id=vehicle_id,
            prediction_id=latest_prediction.get("prediction_id"),
            prediction_proba=explanation["prediction_proba"],
            risk_level=explanation["risk_level"],
            top_factors=top_factors,
            explanation_text=explanation_text,
            timestamp=latest_prediction.get("timestamp")
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate explanation: {str(e)}"
        )
