"""
Health Check and Metrics Endpoints
===================================
API endpoints for monitoring and health checks.

Endpoints:
- GET /health - API health check
- GET /metrics - Model performance metrics
"""

from fastapi import APIRouter, Request
from datetime import datetime
import time

from api.schemas.health import HealthResponse, MetricsResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check(api_request: Request):
    """
    Health check endpoint for monitoring and load balancers.
    
    Returns current status of the API and model loading state.
    
    Args:
        api_request: FastAPI request object
    
    Returns:
        HealthResponse with status, model state, and uptime
    """
    try:
        # Get pipeline from app state
        pipeline = api_request.app.state.pipeline
        
        # Check if model is loaded
        model_loaded = pipeline is not None and pipeline.predictor is not None
        
        # Get model version
        model_version = None
        if model_loaded and pipeline.metadata:
            model_version = pipeline.metadata.get("version", "unknown")
        
        # Calculate uptime
        start_time = api_request.app.state.start_time
        uptime_seconds = time.time() - start_time
        
        # Determine status
        if model_loaded:
            status = "healthy"
        else:
            status = "unhealthy"
        
        return HealthResponse(
            status=status,
            timestamp=datetime.now().isoformat(),
            model_loaded=model_loaded,
            model_version=model_version,
            uptime_seconds=uptime_seconds
        )
        
    except Exception as e:
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.now().isoformat(),
            model_loaded=False,
            model_version=None,
            uptime_seconds=0.0
        )


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics(api_request: Request):
    """
    Get model performance metrics and API statistics.
    
    Returns detailed information about the current model including
    training metrics, version information, and API usage stats.
    
    Args:
        api_request: FastAPI request object
    
    Returns:
        MetricsResponse with model metrics and API statistics
    """
    try:
        # Get pipeline from app state
        pipeline = api_request.app.state.pipeline
        
        if pipeline is None or pipeline.metadata is None:
            return MetricsResponse(
                model_version="unknown",
                training_date=None,
                metrics={},
                predictions_made=api_request.app.state.predictions_count,
                uptime_seconds=time.time() - api_request.app.state.start_time
            )
        
        # Extract metadata
        metadata = pipeline.metadata
        
        # Get model version and training date
        model_version = metadata.get("version", "unknown")
        training_date = metadata.get("training_date", None)
        
        # Get metrics
        metrics = metadata.get("metrics", {})
        
        # Add additional metadata if available
        if "training_samples" in metadata:
            metrics["training_samples"] = metadata["training_samples"]
        if "test_samples" in metadata:
            metrics["test_samples"] = metadata["test_samples"]
        if "optimal_threshold" in metadata:
            metrics["optimal_threshold"] = metadata["optimal_threshold"]
        if "cost_savings" in metadata:
            metrics["cost_savings"] = metadata["cost_savings"]
        
        # Get prediction count and uptime
        predictions_count = api_request.app.state.predictions_count
        start_time = api_request.app.state.start_time
        uptime_seconds = time.time() - start_time
        
        return MetricsResponse(
            model_version=model_version,
            training_date=training_date,
            metrics=metrics,
            predictions_made=predictions_count,
            uptime_seconds=uptime_seconds
        )
        
    except Exception as e:
        # Return minimal metrics on error
        return MetricsResponse(
            model_version="unknown",
            training_date=None,
            metrics={"error": str(e)},
            predictions_made=0,
            uptime_seconds=0.0
        )
