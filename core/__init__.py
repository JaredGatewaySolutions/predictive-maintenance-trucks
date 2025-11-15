"""
Core Predictive Maintenance Modules
====================================
Business logic for predictive maintenance ML pipeline.

Modules:
- scania_loader: Data ingestion from SCANIA dataset
- risk_predictor: XGBoost-based failure prediction
- explainability_analyzer: SHAP-based explanations
- pipeline: End-to-end pipeline orchestration
- model_manager: Model persistence and versioning
"""

from .scania_loader import load_scania_data, prepare_scania_for_classification
from .risk_predictor import RiskPredictor
from .explainability_analyzer import ExplainabilityAnalyzer
from .pipeline import TrainingPipeline, PredictionPipeline
from .model_manager import ModelManager

__all__ = [
    'load_scania_data',
    'prepare_scania_for_classification',
    'RiskPredictor',
    'ExplainabilityAnalyzer',
    'TrainingPipeline',
    'PredictionPipeline',
    'ModelManager'
]
