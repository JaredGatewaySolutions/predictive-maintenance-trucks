"""
Prediction Endpoints
====================
API endpoints for vehicle failure predictions.

Endpoints:
- POST /api/v1/predict - Single vehicle prediction
- POST /api/v1/predict/batch - Multiple vehicle predictions
- GET /api/v1/predictions/{vehicle_id} - Retrieve past predictions

FEATURE NAMING:
- API accepts both Scania codes (171_0) and M1 Abrams names (ENGINE_HOURS)
- Auto-detects format and converts to model format (Scania codes)
- Responses include friendly M1 Abrams feature names for explanations
"""

from fastapi import APIRouter, HTTPException, Request
from datetime import datetime
import pandas as pd
import json
import uuid
from pathlib import Path
from typing import List
import logging

# Import feature mapper for name conversion
from core.feature_mapper import (
    convert_to_model_format,
    auto_detect_format,
    SCANIA_TO_ABRAMS,
    get_feature_info
)

# Configure logging
logger = logging.getLogger(__name__)

from api.schemas.prediction import (
    SinglePredictionRequest,
    BatchPredictionRequest,
    PredictionResponse,
    BatchPredictionResponse,
    PredictionHistory
)

router = APIRouter(prefix="/api/v1", tags=["predictions"])

# Directory for storing predictions and fleets
PREDICTIONS_DIR = Path("data/predictions")
PREDICTIONS_DIR.mkdir(parents=True, exist_ok=True)

FLEETS_DIR = Path("data/fleets")
FLEETS_DIR.mkdir(parents=True, exist_ok=True)
FLEETS_FILE = FLEETS_DIR / "fleets.json"


def generate_prediction_id() -> str:
    """Generate unique prediction ID."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"pred_{timestamp}_{unique_id}"


def generate_fleet_id() -> str:
    """Generate unique fleet ID."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"fleet_{timestamp}_{unique_id}"


def load_fleets():
    """Load fleets data from JSON file."""
    if not FLEETS_FILE.exists():
        return {"fleets": []}
    
    try:
        with open(FLEETS_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading fleets: {e}")
        return {"fleets": []}


def save_fleet(fleet_data: dict):
    """Save fleet data to JSON file."""
    try:
        fleets = load_fleets()
        fleets["fleets"].append(fleet_data)
        
        with open(FLEETS_FILE, 'w') as f:
            json.dump(fleets, f, indent=2)
        
        logger.info(f"✓ Fleet saved: {fleet_data['fleet_name']} ({fleet_data['vehicle_count']} vehicles)")
    except Exception as e:
        logger.error(f"Error saving fleet: {e}")


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
    
    Accepts features in either format:
    - M1 Abrams names (ENGINE_HOURS, FAULT_CODES, etc.)
    - Scania codes (171_0, 666_0, etc.)
    
    Auto-detects format and converts to model format internally.
    
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
        
        # Convert features dict to pandas DataFrame (needed for conversion)
        vehicle_df = pd.DataFrame([request.features])
        
        # Auto-detect format and convert to model format (Scania codes)
        try:
            vehicle_df = convert_to_model_format(vehicle_df, auto_detect=True)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Feature format error: {str(e)}. Ensure all 20 required features are present."
            )
        
        # Convert back to Series for prediction
        vehicle_series = vehicle_df.iloc[0]
        
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
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )


@router.post("/predict/batch", response_model=BatchPredictionResponse)
async def predict_batch(request: BatchPredictionRequest, api_request: Request):
    """
    Predict failure risk for multiple vehicles.
    
    Accepts features in either format:
    - M1 Abrams names (ENGINE_HOURS, FAULT_CODES, etc.)
    - Scania codes (171_0, 666_0, etc.)
    
    Auto-detects format and converts to model format internally.
    
    Args:
        request: Batch prediction request with list of vehicles
        api_request: FastAPI request object
    
    Returns:
        BatchPredictionResponse with list of predictions
    """
    try:
        logger.info("="*80)
        logger.info(f"📦 BATCH PREDICTION REQUEST RECEIVED")
        logger.info(f"   Total vehicles: {len(request.vehicles)}")
        logger.info("="*80)
        
        # Get pipeline from app state
        pipeline = api_request.app.state.pipeline
        
        if pipeline is None or pipeline.predictor is None:
            logger.error("❌ Model not loaded - service unavailable")
            raise HTTPException(
                status_code=503,
                detail="Model not loaded. Service unavailable."
            )
        
        predictions = []
        errors = []
        
        # Get expected features from model metadata
        expected_features = None
        if pipeline.metadata and 'features' in pipeline.metadata:
            expected_features = pipeline.metadata['features']
            logger.info(f"📋 Model expects {len(expected_features)} features")
        
        # Detect format from first vehicle
        if request.vehicles:
            first_vehicle_df = pd.DataFrame([request.vehicles[0].features])
            detected_format = auto_detect_format(first_vehicle_df)
            logger.info(f"📊 Detected feature format: {detected_format.upper()}")
            logger.info(f"   Features in first vehicle: {len(request.vehicles[0].features)}")
            logger.info(f"   Feature names sample: {list(request.vehicles[0].features.keys())[:5]}...")
        
        # Process each vehicle
        for idx, vehicle_request in enumerate(request.vehicles, 1):
            try:
                logger.info(f"🔄 Processing vehicle {idx}/{len(request.vehicles)}: {vehicle_request.vehicle_id}")
                
                # Convert features to pandas DataFrame (needed for conversion)
                vehicle_df = pd.DataFrame([vehicle_request.features])
                logger.info(f"   Input features: {vehicle_df.shape[1]} columns")
                
                # Auto-detect format and convert to model format with padding
                try:
                    vehicle_df = convert_to_model_format(
                        vehicle_df, 
                        auto_detect=True,
                        pad_missing_features=True,
                        expected_features=expected_features
                    )
                    logger.info(f"   Converted to model format: {vehicle_df.shape[1]} features")
                except Exception as e:
                    error_msg = f"Feature conversion failed for {vehicle_request.vehicle_id}: {str(e)}"
                    logger.warning(f"⚠️  {error_msg}")
                    errors.append({"vehicle_id": vehicle_request.vehicle_id, "error": error_msg})
                    continue
                
                # Convert to Series for prediction
                vehicle_series = vehicle_df.iloc[0]
                
                # Make prediction
                logger.info(f"   Making prediction...")
                result = pipeline.predict_single(vehicle_series)
                logger.info(f"   ✓ Prediction: {result['prediction']}, Probability: {result['probability']:.3f}, Risk: {result['risk_level']}")
                
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
                error_msg = f"Error predicting vehicle {vehicle_request.vehicle_id}: {str(e)}"
                logger.error(f"❌ {error_msg}")
                errors.append({"vehicle_id": vehicle_request.vehicle_id, "error": error_msg})
                continue
        
        logger.info("="*80)
        logger.info(f"✅ BATCH PREDICTION COMPLETE")
        logger.info(f"   Successful: {len(predictions)}/{len(request.vehicles)}")
        if errors:
            logger.warning(f"   Failed: {len(errors)}/{len(request.vehicles)}")
            for error in errors:
                logger.warning(f"      - {error['vehicle_id']}: {error['error']}")
        logger.info("="*80)
        
        # If no predictions succeeded, return error
        if not predictions and errors:
            error_details = "\n".join([f"{e['vehicle_id']}: {e['error']}" for e in errors[:3]])
            raise HTTPException(
                status_code=400,
                detail=f"All predictions failed. First errors:\n{error_details}"
            )
        
        # Save fleet metadata if fleet_name is provided
        if request.fleet_name and predictions:
            fleet_id = generate_fleet_id()
            fleet_data = {
                "fleet_id": fleet_id,
                "fleet_name": request.fleet_name,
                "upload_timestamp": datetime.now().isoformat(),
                "vehicle_count": len(predictions),
                "vehicle_ids": [p.vehicle_id for p in predictions],
                "risk_summary": {
                    "high": sum(1 for p in predictions if p.risk_level == "HIGH"),
                    "medium": sum(1 for p in predictions if p.risk_level == "MEDIUM"),
                    "low": sum(1 for p in predictions if p.risk_level == "LOW")
                }
            }
            save_fleet(fleet_data)
            logger.info(f"🚢 Fleet saved: {fleet_id}")
        
        # Build batch response
        batch_response = BatchPredictionResponse(
            predictions=predictions,
            total_count=len(predictions),
            timestamp=datetime.now().isoformat()
        )
        
        return batch_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Batch prediction failed with exception: {str(e)}", exc_info=True)
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


@router.get("/fleets")
async def get_fleets():
    """
    Get all available fleets.
    
    Returns:
        List of fleets with metadata
    """
    try:
        fleets_data = load_fleets()
        # Sort by upload_timestamp descending (most recent first)
        fleets_list = sorted(
            fleets_data.get("fleets", []),
            key=lambda x: x.get("upload_timestamp", ""),
            reverse=True
        )
        
        return {
            "fleets": fleets_list,
            "total_count": len(fleets_list)
        }
    except Exception as e:
        logger.error(f"Error retrieving fleets: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve fleets: {str(e)}"
        )


@router.get("/fleets/{fleet_id}/predictions")
async def get_fleet_predictions(fleet_id: str):
    """
    Get all predictions for a specific fleet.
    
    Args:
        fleet_id: Fleet identifier
    
    Returns:
        All predictions for vehicles in the fleet
    """
    try:
        # Load fleets
        fleets_data = load_fleets()
        fleet = next((f for f in fleets_data.get("fleets", []) if f["fleet_id"] == fleet_id), None)
        
        if not fleet:
            raise HTTPException(
                status_code=404,
                detail=f"Fleet {fleet_id} not found"
            )
        
        # Load predictions for all vehicles in the fleet
        predictions = []
        for vehicle_id in fleet.get("vehicle_ids", []):
            file_path = PREDICTIONS_DIR / f"{vehicle_id}.json"
            if file_path.exists():
                with open(file_path, 'r') as f:
                    vehicle_data = json.load(f)
                    # Get the most recent prediction for this vehicle
                    vehicle_preds = vehicle_data.get("predictions", [])
                    if vehicle_preds:
                        predictions.append(vehicle_preds[-1])  # Most recent
        
        return {
            "fleet": fleet,
            "predictions": predictions,
            "total_count": len(predictions)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving fleet predictions: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve fleet predictions: {str(e)}"
        )
