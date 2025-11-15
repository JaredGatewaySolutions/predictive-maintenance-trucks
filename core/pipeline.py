#!/usr/bin/env python3
"""
Pipeline Orchestrator for Predictive Maintenance
=================================================
End-to-end orchestration of training and prediction workflows.

Features:
- TrainingPipeline: Complete training workflow with data loading, training, evaluation
- PredictionPipeline: Inference pipeline for new vehicle data
- Integration with ModelManager for persistence

Author: Predictive Maintenance for Army XEM
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from typing import Dict, Optional, List, Any, Tuple
import warnings
from datetime import datetime
from pathlib import Path

from .scania_loader import load_scania_data, prepare_scania_for_classification
from .risk_predictor import RiskPredictor
from .explainability_analyzer import ExplainabilityAnalyzer
from .model_manager import ModelManager

warnings.filterwarnings("ignore")


class TrainingPipeline:
    """
    End-to-end training pipeline for predictive maintenance.
    
    Workflow:
    1. Load and prepare data
    2. Train risk prediction model
    3. Evaluate model performance
    4. Calculate cost analysis
    5. Save model with metadata
    """
    
    def __init__(
        self,
        data_dir: str = "data",
        models_dir: str = "data/models",
        handle_imbalance: bool = True,
        calibrate_probabilities: bool = True
    ):
        """
        Initialize training pipeline.
        
        Args:
            data_dir: Directory containing training data
            models_dir: Directory for saving models
            handle_imbalance: Use scale_pos_weight for imbalance
            calibrate_probabilities: Calibrate predicted probabilities
        """
        self.data_dir = data_dir
        self.handle_imbalance = handle_imbalance
        self.calibrate_probabilities = calibrate_probabilities
        self.model_manager = ModelManager(models_dir=models_dir)
        
        self.predictor = None
        self.analyzer = None
        self.feature_names = None
        
        print("="*80)
        print("TRAINING PIPELINE INITIALIZED")
        print("="*80)
        print(f"Data directory: {data_dir}")
        print(f"Models directory: {models_dir}")
        print(f"Imbalance handling: {handle_imbalance}")
        print(f"Probability calibration: {calibrate_probabilities}")
    
    def load_data(
        self,
        test_size: float = 0.2,
        n_samples: Optional[int] = None,
        random_state: int = 42
    ) -> Dict[str, Any]:
        """
        Load and prepare data for training.
        
        Args:
            test_size: Proportion of data for testing
            n_samples: Number of samples to use (None = all data)
            random_state: Random seed for reproducibility
        
        Returns:
            Dictionary with train/test splits
        """
        print("\n" + "="*80)
        print("STEP 1: DATA LOADING AND PREPARATION")
        print("="*80)
        
        # Load data
        data = load_scania_data(data_dir=self.data_dir)
        
        if 'train_operational' not in data:
            raise ValueError(f"Failed to load data from {self.data_dir}")
        
        # Prepare for classification
        X, y, vehicle_ids = prepare_scania_for_classification(data)
        
        # Sample if requested
        if n_samples and n_samples < len(X):
            print(f"\n📊 Sampling {n_samples} vehicles...")
            sample_idx = np.random.choice(len(X), size=n_samples, replace=False)
            X = X.iloc[sample_idx]
            y = y.iloc[sample_idx]
            vehicle_ids = vehicle_ids.iloc[sample_idx]
            print(f"   Sampled: {X.shape}")
            print(f"   Failures: {y.sum()} ({y.sum()/len(y)*100:.1f}%)")
        
        # Store feature names
        self.feature_names = list(X.columns)
        
        # Train/test split
        X_train, X_test, y_train, y_test, ids_train, ids_test = train_test_split(
            X, y, vehicle_ids, test_size=test_size, random_state=random_state, stratify=y
        )
        
        print(f"\n✓ Data prepared:")
        print(f"   Total samples: {len(X):,}")
        print(f"   Features: {X.shape[1]}")
        print(f"   Training: {X_train.shape[0]:,} vehicles ({len(X_train)/len(X)*100:.0f}%)")
        print(f"   Test: {X_test.shape[0]:,} vehicles ({len(X_test)/len(X)*100:.0f}%)")
        print(f"   Class distribution:")
        print(f"     - Healthy: {(y == 0).sum():,} ({(y == 0).sum()/len(y)*100:.1f}%)")
        print(f"     - Failed: {(y == 1).sum():,} ({(y == 1).sum()/len(y)*100:.1f}%)")
        
        return {
            'X_train': X_train,
            'X_test': X_test,
            'y_train': y_train,
            'y_test': y_test,
            'ids_train': ids_train,
            'ids_test': ids_test,
            'feature_names': self.feature_names
        }
    
    def train_model(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        **xgb_params
    ) -> RiskPredictor:
        """
        Train risk prediction model.
        
        Args:
            X_train: Training features
            y_train: Training labels
            **xgb_params: Additional XGBoost parameters
        
        Returns:
            Trained RiskPredictor
        """
        print("\n" + "="*80)
        print("STEP 2: MODEL TRAINING")
        print("="*80)
        
        # Initialize predictor
        self.predictor = RiskPredictor(
            handle_imbalance=self.handle_imbalance,
            calibrate_probabilities=self.calibrate_probabilities
        )
        
        # Train
        self.predictor.train(X_train, y_train, **xgb_params)
        
        print("\n✓ Model training completed")
        
        return self.predictor
    
    def evaluate_model(
        self,
        X_test: pd.DataFrame,
        y_test: pd.Series
    ) -> Dict[str, Any]:
        """
        Evaluate trained model.
        
        Args:
            X_test: Test features
            y_test: Test labels
        
        Returns:
            Evaluation results
        """
        print("\n" + "="*80)
        print("STEP 3: MODEL EVALUATION")
        print("="*80)
        
        if self.predictor is None:
            raise ValueError("Model not trained. Call train_model() first.")
        
        # Evaluate
        eval_results = self.predictor.evaluate(X_test, y_test)
        
        # Cost analysis
        cost_results = self.predictor.calculate_scania_cost(
            y_test,
            eval_results['y_pred']
        )
        
        # Optimal threshold
        threshold_results = self.predictor.find_optimal_threshold(X_test, y_test)
        
        print("\n✓ Evaluation completed")
        
        return {
            'eval_results': eval_results,
            'cost_results': cost_results,
            'threshold_results': threshold_results
        }
    
    def initialize_explainability(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_test: pd.DataFrame,
        background_samples: int = 100
    ) -> ExplainabilityAnalyzer:
        """
        Initialize explainability analyzer.
        
        Args:
            X_train: Training features
            y_train: Training labels
            X_test: Test features
            background_samples: Number of samples for SHAP background
        
        Returns:
            Initialized ExplainabilityAnalyzer
        """
        print("\n" + "="*80)
        print("STEP 4: EXPLAINABILITY INITIALIZATION")
        print("="*80)
        
        if self.predictor is None:
            raise ValueError("Model not trained. Call train_model() first.")
        
        # Initialize analyzer
        self.analyzer = ExplainabilityAnalyzer(
            model=self.predictor.model,
            X_train=X_train,
            y_train=y_train,
            X_test=X_test
        )
        
        # Initialize SHAP
        self.analyzer.initialize_shap(background_samples=background_samples)
        
        print("\n✓ Explainability initialized")
        
        return self.analyzer
    
    def save_model(
        self,
        metadata: Optional[Dict] = None,
        version_name: Optional[str] = None
    ) -> str:
        """
        Save trained model with metadata.
        
        Args:
            metadata: Additional metadata to save
            version_name: Custom version name
        
        Returns:
            Version name of saved model
        """
        print("\n" + "="*80)
        print("STEP 5: MODEL PERSISTENCE")
        print("="*80)
        
        if self.predictor is None:
            raise ValueError("Model not trained. Call train_model() first.")
        
        # Build metadata
        if metadata is None:
            metadata = {}
        
        metadata.update({
            "model_type": "RiskPredictor",
            "pipeline_version": "1.0",
            "training_date": datetime.now().isoformat(),
            "features": self.feature_names,
            "handle_imbalance": self.handle_imbalance,
            "calibrate_probabilities": self.calibrate_probabilities
        })
        
        # Save model
        version = self.model_manager.save_model(
            model=self.predictor,
            metadata=metadata,
            version_name=version_name
        )
        
        return version
    
    def run_full_pipeline(
        self,
        test_size: float = 0.2,
        n_samples: Optional[int] = None,
        initialize_shap: bool = True,
        save_model: bool = True,
        **xgb_params
    ) -> Dict[str, Any]:
        """
        Run complete training pipeline.
        
        Args:
            test_size: Test set proportion
            n_samples: Number of samples (None = all)
            initialize_shap: Initialize SHAP explainability
            save_model: Save trained model
            **xgb_params: XGBoost parameters
        
        Returns:
            Complete results dictionary
        """
        print("\n" + "╔" + "="*78 + "╗")
        print("║" + "FULL TRAINING PIPELINE".center(78) + "║")
        print("╚" + "="*78 + "╝")
        
        # Step 1: Load data
        data_splits = self.load_data(test_size=test_size, n_samples=n_samples)
        
        # Step 2: Train model
        self.train_model(data_splits['X_train'], data_splits['y_train'], **xgb_params)
        
        # Step 3: Evaluate
        evaluation = self.evaluate_model(data_splits['X_test'], data_splits['y_test'])
        
        # Step 4: Initialize explainability
        if initialize_shap:
            self.initialize_explainability(
                data_splits['X_train'],
                data_splits['y_train'],
                data_splits['X_test']
            )
        
        # Step 5: Save model
        version = None
        if save_model:
            metadata = {
                "metrics": {
                    "accuracy": float(evaluation['eval_results']['accuracy']),
                    "auc_roc": float(evaluation['eval_results']['auc_roc']),
                    "recall": float(evaluation['eval_results']['recall']),
                    "precision": float(evaluation['eval_results']['precision'])
                },
                "training_samples": len(data_splits['X_train']),
                "test_samples": len(data_splits['X_test']),
                "optimal_threshold": float(evaluation['threshold_results']['optimal_threshold']),
                "cost_savings": float(evaluation['threshold_results']['savings'])
            }
            version = self.save_model(metadata=metadata)
        
        print("\n" + "╔" + "="*78 + "╗")
        print("║" + "PIPELINE COMPLETED SUCCESSFULLY".center(78) + "║")
        print("╚" + "="*78 + "╝\n")
        
        return {
            'version': version,
            'predictor': self.predictor,
            'analyzer': self.analyzer,
            'data_splits': data_splits,
            'evaluation': evaluation
        }


class PredictionPipeline:
    """
    Inference pipeline for making predictions on new vehicle data.
    
    Workflow:
    1. Load trained model
    2. Preprocess input data
    3. Make predictions
    4. Generate explanations (optional)
    """
    
    def __init__(self, models_dir: str = "data/models"):
        """
        Initialize prediction pipeline.
        
        Args:
            models_dir: Directory containing saved models
        """
        self.models_dir = models_dir
        self.model_manager = ModelManager(models_dir=models_dir)
        self.predictor = None
        self.metadata = None
        
        print("="*80)
        print("PREDICTION PIPELINE INITIALIZED")
        print("="*80)
    
    def load_model(self, version: Optional[str] = None):
        """
        Load trained model.
        
        Args:
            version: Model version (None = latest)
        """
        print(f"\nLoading model...")
        
        loaded = self.model_manager.load_model(version=version)
        self.predictor = loaded['model']
        self.metadata = loaded.get('metadata', {})
        
        print(f"✓ Model loaded successfully")
        if self.metadata:
            print(f"   Version: {self.metadata.get('version', 'unknown')}")
            print(f"   Training date: {self.metadata.get('training_date', 'unknown')}")
            metrics = self.metadata.get('metrics', {})
            if metrics:
                print(f"   Accuracy: {metrics.get('accuracy', 'N/A'):.3f}")
                print(f"   AUC-ROC: {metrics.get('auc_roc', 'N/A'):.3f}")
    
    def predict_single(
        self,
        vehicle_data: pd.Series,
        return_explanation: bool = False
    ) -> Dict[str, Any]:
        """
        Predict failure risk for a single vehicle.
        
        Args:
            vehicle_data: Vehicle feature data (Series)
            return_explanation: Include SHAP explanation
        
        Returns:
            Prediction dictionary
        """
        if self.predictor is None:
            raise ValueError("Model not loaded. Call load_model() first.")
        
        # Convert to DataFrame
        X = pd.DataFrame([vehicle_data])
        
        # Predict
        y_pred = self.predictor.predict(X)[0]
        y_pred_proba = self.predictor.predict_proba(X)[0]
        
        result = {
            'prediction': int(y_pred),
            'probability': float(y_pred_proba),
            'risk_level': self._get_risk_level(y_pred_proba),
            'timestamp': datetime.now().isoformat()
        }
        
        return result
    
    def predict_batch(
        self,
        vehicles_data: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Predict failure risk for multiple vehicles.
        
        Args:
            vehicles_data: DataFrame of vehicle features
        
        Returns:
            DataFrame with predictions
        """
        if self.predictor is None:
            raise ValueError("Model not loaded. Call load_model() first.")
        
        # Predict
        y_pred = self.predictor.predict(vehicles_data)
        y_pred_proba = self.predictor.predict_proba(vehicles_data)
        
        # Build results DataFrame
        results = vehicles_data.copy()
        results['prediction'] = y_pred
        results['probability'] = y_pred_proba
        results['risk_level'] = results['probability'].apply(self._get_risk_level)
        results['timestamp'] = datetime.now().isoformat()
        
        return results
    
    def _get_risk_level(self, probability: float) -> str:
        """
        Categorize risk level based on probability.
        
        Args:
            probability: Failure probability
        
        Returns:
            Risk level string
        """
        if probability >= 0.7:
            return "HIGH"
        elif probability >= 0.4:
            return "MEDIUM"
        else:
            return "LOW"


if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║                      PIPELINE ORCHESTRATOR - DEMO                            ║
    ║                                                                              ║
    ║  End-to-end orchestration of training and prediction:                       ║
    ║  • TrainingPipeline: Complete training workflow                             ║
    ║  • PredictionPipeline: Inference on new data                                ║
    ║  • Integration with ModelManager for persistence                            ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    
    USAGE EXAMPLE - TRAINING:
    =========================
    
    from core.pipeline import TrainingPipeline
    
    # Initialize and run full pipeline
    pipeline = TrainingPipeline()
    results = pipeline.run_full_pipeline(
        n_samples=5000,
        test_size=0.2,
        initialize_shap=True,
        save_model=True
    )
    
    print(f"Model version: {results['version']}")
    print(f"Accuracy: {results['evaluation']['eval_results']['accuracy']:.3f}")
    
    
    USAGE EXAMPLE - PREDICTION:
    ===========================
    
    from core.pipeline import PredictionPipeline
    import pandas as pd
    
    # Initialize pipeline and load model
    pipeline = PredictionPipeline()
    pipeline.load_model()  # Loads latest model
    
    # Predict single vehicle
    vehicle_data = pd.Series({...})  # Vehicle features
    prediction = pipeline.predict_single(vehicle_data)
    print(f"Risk: {prediction['risk_level']} ({prediction['probability']:.2%})")
    
    # Predict batch
    vehicles_df = pd.DataFrame([...])
    predictions = pipeline.predict_batch(vehicles_df)
    
    ══════════════════════════════════════════════════════════════════════════════
    
    KEY FEATURES:
    • Complete end-to-end orchestration
    • Automatic model persistence with versioning
    • Integrated explainability (SHAP)
    • Batch and single predictions
    • Risk level categorization (HIGH/MEDIUM/LOW)
    
    Perfect for microservices: Train once, deploy everywhere
    """)
