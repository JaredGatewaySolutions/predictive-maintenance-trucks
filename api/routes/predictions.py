"""
Prediction Endpoints
====================
API endpoints for vehicle failure predictions.

Endpoints:
- POST /api/v1/predict - Single vehicle prediction
- POST /api/v1/predict/batch - Multiple vehicle predictions
- GET /api/v1/predictions/{vehicle_id} - Retrieve past predictions
"""

from fastapi import APIRouter, HTTPException, Request
from datetime import datetime
import pandas as pd
import json
import uuid
from pathlib import Path
from typing import List

from api.schemas.prediction import (
    SinglePredictionRequest,
    BatchPredictionRequest,
    PredictionResponse,
    BatchPredictionResponse,
    PredictionHistory
)

router = APIRouter(prefix="/api/v1", tags=["predictions"])

# Directory for storing predictions
PREDICTIONS_DIR = Path("data/predictions")
PREDICTIONS_DIR.mkdir(parents=True, exist_ok=True)


def generate_prediction_id() -> str:
    """Generate unique prediction ID."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"pred_{timestamp}_{unique_id}"


def save_prediction(prediction: dict, vehicle_id: str = None):
    """
    Save prediction to JSON file.
    
    Args:
        prediction: Prediction dictionary
        vehicle_id: Vehicle identifier (optional)
    """
    try:
        # Save by vehicle_id if provided
        if vehicle_id:
            file_path = PREDICTIONS_DIR / f"{vehicle_id}.json"
            
            # Load existing predictions if file exists
            if file_path.exists():
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    predictions_list = data.get("predictions", [])
            else:
                predictions_list = []
            
            # Append new prediction
            predictions_list.append(prediction)
            
            # Save updated predictions
            with open(file_path, 'w') as f:
                json.dump({
                    "vehicle_id": vehicle_id,
                    "predictions": predictions_list,
                    "count": len(predictions_list),
                    "last_updated": datetime.now().isoformat()
                }, f, indent=2)
        
        # Also save individual prediction file
        pred_file = PREDICTIONS_DIR / f"{prediction['prediction_id']}.json"
        with open(pred_file, 'w') as f:
            json.dump(prediction, f, indent=2)
            
    except Exception as e:
        # Log error but don't fail the request
        print(f"Warning: Failed to save prediction: {e}")


@router.post("/predict", response_model=PredictionResponse)
async def predict_single(request: SinglePredictionRequest, api_request: Request):
    """
    Predict failure risk for a single vehicle.
    
    Args:
        request: Single prediction request with vehicle features
        api_request: FastAPI request object (for accessing app state)
    
    Returns:
        PredictionResponse with prediction, probability, and risk level
    """
    try:
        # Get pipeline from app state
        pipeline = api_request.app.state.pipeline
        
        if pipeline is None or pipeline.predictor is None:
            raise HTTPException(
                status_code=503,
                detail="Model not loaded. Service unavailable."
            )
        
        # Convert features dict to pandas Series
        vehicle_series = pd.Series(request.features)
        
        # Make prediction
        result = pipeline.predict_single(vehicle_series)
        
        # Generate prediction ID
        prediction_id = generate_prediction_id()
        
        # Get model version from metadata
        model_version = pipeline.metadata.get("version", "unknown") if pipeline.metadata else "unknown"
        
        # Build response
        response = PredictionResponse(
            prediction_id=prediction_id,
            vehicle_id=request.vehicle_id,
            prediction=result["prediction"],
            probability=result["probability"],
            risk_level=result["risk_level"],
            timestamp=result["timestamp"],
            model_version=model_version
        )
        
        # Save prediction
        prediction_dict = response.dict()
        prediction_dict["features"] = request.features  # Include features for later explanation
        save_prediction(prediction_dict, request.vehicle_id)
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )


@router.post("/predict/batch", response_model=BatchPredictionResponse)
async def predict_batch(request: BatchPredictionRequest, api_request: Request):
    """
    Predict failure risk for multiple vehicles.
    
    Args:
        request: Batch prediction request with list of vehicles
        api_request: FastAPI request object
    
    Returns:
        BatchPredictionResponse with list of predictions
    """
    try:
        # Get pipeline from app state
        pipeline = api_request.app.state.pipeline
        
        if pipeline is None or pipeline.predictor is None:
            raise HTTPException(
                status_code=503,
                detail="Model not loaded. Service unavailable."
            )
        
        predictions = []
        
        # Process each vehicle
        for vehicle_request in request.vehicles:
            try:
                # Convert features to pandas Series
                vehicle_series = pd.Series(vehicle_request.features)
                
                # Make prediction
                result = pipeline.predict_single(vehicle_series)
                
                # Generate prediction ID
                prediction_id = generate_prediction_id()
                
                # Get model version
                model_version = pipeline.metadata.get("version", "unknown") if pipeline.metadata else "unknown"
                
                # Build response
                prediction_response = PredictionResponse(
                    prediction_id=prediction_id,
                    vehicle_id=vehicle_request.vehicle_id,
                    prediction=result["prediction"],
                    probability=result["probability"],
                    risk_level=result["risk_level"],
                    timestamp=result["timestamp"],
                    model_version=model_version
                )
                
                predictions.append(prediction_response)
                
                # Save prediction
                prediction_dict = prediction_response.dict()
                prediction_dict["features"] = vehicle_request.features
                save_prediction(prediction_dict, vehicle_request.vehicle_id)
                
            except Exception as e:
                # Log error but continue with other vehicles
                print(f"Error predicting vehicle {vehicle_request.vehicle_id}: {e}")
                continue
        
        # Build batch response
        batch_response = BatchPredictionResponse(
            predictions=predictions,
            total_count=len(predictions),
            timestamp=datetime.now().isoformat()
        )
        
        return batch_response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Batch prediction failed: {str(e)}"
        )


@router.get("/predictions/{vehicle_id}", response_model=PredictionHistory)
async def get_predictions(vehicle_id: str):
    """
    Retrieve past predictions for a specific vehicle.
    
    Args:
        vehicle_id: Vehicle identifier
    
    Returns:
        PredictionHistory with all past predictions for the vehicle
    """
    try:
        file_path = PREDICTIONS_DIR / f"{vehicle_id}.json"
        
        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"No predictions found for vehicle {vehicle_id}"
            )
        
        # Load predictions
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        predictions_list = data.get("predictions", [])
        
        if not predictions_list:
            raise HTTPException(
                status_code=404,
                detail=f"No predictions found for vehicle {vehicle_id}"
            )
        
        # Build response
        response = PredictionHistory(
            vehicle_id=vehicle_id,
            predictions=[PredictionResponse(**pred) for pred in predictions_list],
            count=len(predictions_list),
            first_prediction=predictions_list[0]["timestamp"] if predictions_list else None,
            last_prediction=predictions_list[-1]["timestamp"] if predictions_list else None
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve predictions: {str(e)}"
        )
