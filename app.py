#!/usr/bin/env python3
"""
Predictive Maintenance API
===========================
FastAPI application for vehicle failure predictions.

Features:
- Load trained model at startup
- Single and batch predictions
- SHAP-based explanations
- Health checks and metrics
- CORS support for frontend integration

Author: Predictive Maintenance for Army XEM
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import logging
from pathlib import Path

from core.pipeline import PredictionPipeline
from core.explainability_analyzer import ExplainabilityAnalyzer
from api.routes import predictions_router, explanations_router, health_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Predictive Maintenance API",
    description="REST API for vehicle failure predictions with SHAP explanations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["tanks.gatewaysolutions.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """
    Initialize model and services at application startup.
    
    This runs once when the API starts up:
    1. Load the trained model using PredictionPipeline
    2. Initialize SHAP explainability analyzer (optional)
    3. Set up application state
    """
    logger.info("="*80)
    logger.info("STARTING PREDICTIVE MAINTENANCE API")
    logger.info("="*80)
    
    try:
        # Initialize application state
        app.state.start_time = time.time()
        app.state.predictions_count = 0
        
        # Initialize prediction pipeline
        logger.info("Loading prediction model...")
        pipeline = PredictionPipeline()
        
        # Load the latest trained model
        pipeline.load_model()
        
        # Store pipeline in app state
        app.state.pipeline = pipeline
        
        logger.info("✓ Model loaded successfully")
        if pipeline.metadata:
            logger.info(f"  Model version: {pipeline.metadata.get('version', 'unknown')}")
            logger.info(f"  Training date: {pipeline.metadata.get('training_date', 'unknown')}")
            metrics = pipeline.metadata.get('metrics', {})
            if metrics:
                logger.info(f"  Accuracy: {metrics.get('accuracy', 'N/A')}")
                logger.info(f"  AUC-ROC: {metrics.get('auc_roc', 'N/A')}")
        
        # Initialize explainability analyzer with training data
        logger.info("\nInitializing SHAP explainability analyzer...")
        try:
            # Load training data from model
            loaded = pipeline.model_manager.load_model(include_training_data=True)
            training_data = loaded.get('training_data')
            
            if training_data and 'X_train' in training_data and 'y_train' in training_data:
                # Initialize analyzer with training data
                X_train = training_data['X_train']
                y_train = training_data['y_train']
                
                logger.info(f"  Found training data sample: {X_train.shape[0]} samples")
                
                # Create ExplainabilityAnalyzer
                analyzer = ExplainabilityAnalyzer(
                    model=pipeline.predictor.model,
                    X_train=X_train,
                    y_train=y_train
                )
                
                # Initialize SHAP (this may take a few seconds)
                analyzer.initialize_shap(background_samples=min(100, len(X_train)))
                
                app.state.analyzer = analyzer
                logger.info("✓ SHAP explainability analyzer initialized successfully")
            else:
                logger.warning("⚠ No training data found with model")
                logger.warning("  SHAP explanations will be unavailable")
                logger.warning("  Re-train the model to include training data sample")
                app.state.analyzer = None
                
        except Exception as e:
            logger.warning(f"⚠ Could not initialize explainability analyzer: {e}")
            logger.warning("  SHAP explanations will be unavailable")
            app.state.analyzer = None
        
        logger.info("\n" + "="*80)
        logger.info("API READY - Listening for requests")
        logger.info("="*80)
        logger.info("Documentation: http://localhost:8000/docs")
        logger.info("Health check: http://localhost:8000/health")
        logger.info("="*80 + "\n")
        
    except Exception as e:
        logger.error(f"✗ STARTUP FAILED: {e}")
        logger.error("  API will not be able to serve predictions")
        
        # Set state to indicate failure
        app.state.pipeline = None
        app.state.analyzer = None
        app.state.start_time = time.time()
        app.state.predictions_count = 0


@app.on_event("shutdown")
async def shutdown_event():
    """
    Cleanup when application shuts down.
    """
    logger.info("\n" + "="*80)
    logger.info("SHUTTING DOWN PREDICTIVE MAINTENANCE API")
    logger.info("="*80)
    
    # Log final statistics
    if hasattr(app.state, 'predictions_count'):
        logger.info(f"Total predictions made: {app.state.predictions_count}")
    
    if hasattr(app.state, 'start_time'):
        uptime = time.time() - app.state.start_time
        logger.info(f"Total uptime: {uptime:.2f} seconds")
    
    logger.info("✓ Shutdown complete")
    logger.info("="*80 + "\n")


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled errors.
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc)
        }
    )


# Middleware to count predictions
@app.middleware("http")
async def count_predictions(request: Request, call_next):
    """
    Middleware to track prediction count.
    """
    # Count prediction requests
    if request.url.path.startswith("/api/v1/predict"):
        app.state.predictions_count += 1
    
    response = await call_next(request)
    return response


# Register routers
app.include_router(predictions_router)
app.include_router(explanations_router)
app.include_router(health_router)


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "name": "Predictive Maintenance API",
        "version": "1.0.0",
        "description": "REST API for vehicle failure predictions with SHAP explanations",
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics",
        "endpoints": {
            "predict_single": "POST /api/v1/predict",
            "predict_batch": "POST /api/v1/predict/batch",
            "get_predictions": "GET /api/v1/predictions/{vehicle_id}",
            "explain": "GET /api/v1/explain/{vehicle_id}",
            "health": "GET /health",
            "metrics": "GET /metrics"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    print("""
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║                    PREDICTIVE MAINTENANCE API                                ║
    ║                                                                              ║
    ║  Starting FastAPI server...                                                  ║
    ║  Documentation: http://localhost:8000/docs                                   ║
    ║  Health check:  http://localhost:8000/health                                 ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload during development
        log_level="info"
    )
