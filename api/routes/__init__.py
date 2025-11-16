"""
API Routes for Predictive Maintenance
======================================
FastAPI route modules for predictions, explanations, and health checks.
"""

from .predictions import router as predictions_router
from .explanations import router as explanations_router
from .health import router as health_router

__all__ = [
    "predictions_router",
    "explanations_router",
    "health_router"
]
