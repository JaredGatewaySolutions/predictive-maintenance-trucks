#!/usr/bin/env python3
"""
Risk Predictor for Predictive Maintenance
==========================================
Focused module for failure risk prediction with:
- XGBoost classifier with imbalance handling
- Cost-sensitive learning (SCANIA cost function)
- Probability calibration

Author: Predictive Maintenance for Army XEM
Use Case: Predict vehicle failure risk with proper imbalance handling
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report, 
    confusion_matrix, 
    roc_auc_score,
    precision_recall_curve,
    roc_curve
)
from sklearn.calibration import CalibratedClassifierCV
import xgboost as xgb
from typing import Dict, Tuple
import warnings

warnings.filterwarnings("ignore")


class RiskPredictor:
    """
    Predictive maintenance risk predictor with imbalance handling.
    
    Features:
    - XGBoost with scale_pos_weight for imbalance
    - Cost-sensitive learning using SCANIA's cost function
    - Probability calibration
    - Comprehensive evaluation metrics
    """
    
    def __init__(self, handle_imbalance=True, calibrate_probabilities=True):
        """
        Initialize risk predictor.
        
        Args:
            handle_imbalance: If True, use scale_pos_weight
            calibrate_probabilities: If True, calibrate predicted probabilities
        """
        self.handle_imbalance = handle_imbalance
        self.calibrate_probabilities = calibrate_probabilities
        self.model = None
        self.calibrated_model = None
        self.scale_pos_weight = None
        
        print("="*80)
        print("RISK PREDICTOR INITIALIZED")
        print("="*80)
        print(f"Imbalance handling: {handle_imbalance}")
        print(f"Probability calibration: {calibrate_probabilities}")
    
    def train(self, X_train, y_train, **xgb_params):
        """
        Train XGBoost model with imbalance handling.
        
        Args:
            X_train: Training features
            y_train: Training labels
            **xgb_params: Additional XGBoost parameters
        """
        print("\n" + "="*80)
        print("TRAINING RISK PREDICTION MODEL")
        print("="*80)
        
        # Calculate scale_pos_weight for imbalance
        if self.handle_imbalance:
            self.scale_pos_weight = (len(y_train) - y_train.sum()) / y_train.sum()
            print(f"Handling class imbalance:")
            print(f"  Negative class: {len(y_train) - y_train.sum()} ({(len(y_train) - y_train.sum())/len(y_train)*100:.1f}%)")
            print(f"  Positive class: {y_train.sum()} ({y_train.sum()/len(y_train)*100:.1f}%)")
            print(f"  Imbalance ratio: {self.scale_pos_weight:.2f}:1")
            print(f"  scale_pos_weight: {self.scale_pos_weight:.2f}")
        
        # Default XGBoost parameters
        default_params = {
            'n_estimators': 100,
            'max_depth': 6,
            'learning_rate': 0.1,
            'random_state': 42,
            'eval_metric': 'logloss',
            'use_label_encoder': False,
            'n_jobs': -1
        }
        
        # Add scale_pos_weight if handling imbalance
        if self.handle_imbalance:
            default_params['scale_pos_weight'] = self.scale_pos_weight
        
        # Override with user params
        default_params.update(xgb_params)
        
        print(f"\nTraining XGBoost with parameters:")
        for key, value in default_params.items():
            print(f"  {key}: {value}")
        
        # Train model
        self.model = xgb.XGBClassifier(**default_params)
        self.model.fit(X_train, y_train)
        
        print("\n✓ Model trained successfully")
        
        # Calibrate probabilities if requested
        if self.calibrate_probabilities:
            print("\nCalibrating probabilities...")
            self.calibrated_model = CalibratedClassifierCV(
                self.model, 
                method='sigmoid', 
                cv=3
            )
            self.calibrated_model.fit(X_train, y_train)
            print("✓ Probabilities calibrated")
    
    def predict(self, X, use_calibrated=None):
        """
        Make predictions.
        
        Args:
            X: Features to predict
            use_calibrated: Use calibrated model (default: use initialization setting)
        
        Returns:
            Predictions (0/1)
        """
        if use_calibrated is None:
            use_calibrated = self.calibrate_probabilities
        
        model = self.calibrated_model if use_calibrated else self.model
        
        if model is None:
            raise ValueError("Model not trained yet. Call train() first.")
        
        return model.predict(X)
    
    def predict_proba(self, X, use_calibrated=None):
        """
        Predict failure probabilities.
        
        Args:
            X: Features to predict
            use_calibrated: Use calibrated model (default: use initialization setting)
        
        Returns:
            Probability of positive class (failure)
        """
        if use_calibrated is None:
            use_calibrated = self.calibrate_probabilities
        
        model = self.calibrated_model if use_calibrated else self.model
        
        if model is None:
            raise ValueError("Model not trained yet. Call train() first.")
        
        return model.predict_proba(X)[:, 1]
    
    def evaluate(self, X_test, y_test, use_calibrated=None):
        """
        Comprehensive model evaluation.
        
        Args:
            X_test: Test features
            y_test: Test labels
            use_calibrated: Use calibrated model
        
        Returns:
            Dictionary of evaluation metrics
        """
        print("\n" + "="*80)
        print("MODEL EVALUATION")
        print("="*80)
        
        if use_calibrated is None:
            use_calibrated = self.calibrate_probabilities
        
        model_type = "Calibrated" if use_calibrated else "Base"
        print(f"Using {model_type} model")
        
        # Predictions
        y_pred = self.predict(X_test, use_calibrated=use_calibrated)
        y_pred_proba = self.predict_proba(X_test, use_calibrated=use_calibrated)
        
        # Metrics
        accuracy = (y_pred == y_test).mean()
        auc_score = roc_auc_score(y_test, y_pred_proba)
        
        print(f"\n📊 Overall Metrics:")
        print(f"  Accuracy: {accuracy:.3f}")
        print(f"  AUC-ROC: {auc_score:.3f}")
        
        # Classification report
        print(f"\n📋 Classification Report:")
        print(classification_report(y_test, y_pred, target_names=['Healthy', 'Failed']))
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        tn, fp, fn, tp = cm.ravel()
        
        print(f"\n🎯 Confusion Matrix:")
        print(f"  True Negatives:  {tn:5d} (Correctly predicted healthy)")
        print(f"  False Positives: {fp:5d} (Predicted failure, actually healthy)")
        print(f"  False Negatives: {fn:5d} (Predicted healthy, actually failed) ⚠️ CRITICAL")
        print(f"  True Positives:  {tp:5d} (Correctly predicted failure)")
        
        # Calculate rates
        if (tn + fp) > 0:
            specificity = tn / (tn + fp)
        else:
            specificity = 0
        
        if (tp + fn) > 0:
            recall = tp / (tp + fn)
        else:
            recall = 0
        
        if (tp + fp) > 0:
            precision = tp / (tp + fp)
        else:
            precision = 0
        
        print(f"\n📈 Key Metrics:")
        print(f"  Recall (Sensitivity):    {recall:.3f} - Catches {recall*100:.1f}% of failures")
        print(f"  Precision:               {precision:.3f} - {precision*100:.1f}% of predictions are correct")
        print(f"  Specificity:             {specificity:.3f} - Correctly identifies {specificity*100:.1f}% of healthy")
        
        return {
            'accuracy': accuracy,
            'auc_roc': auc_score,
            'recall': recall,
            'precision': precision,
            'specificity': specificity,
            'confusion_matrix': cm,
            'y_pred': y_pred,
            'y_pred_proba': y_pred_proba
        }
    
    def calculate_scania_cost(self, y_test, y_pred, class_labels=None):
        """
        Calculate cost using SCANIA's cost function.
        
        From the paper:
        - False negatives (miss failure): 200-500 cost
        - False positives (unnecessary check): 7-10 cost
        
        This reflects real-world: Missing a failure is MUCH more expensive
        than an unnecessary maintenance check.
        
        Args:
            y_test: True labels
            y_pred: Predicted labels (or probabilities for threshold analysis)
            class_labels: If provided, assumes y_pred are probabilities for window classes
        
        Returns:
            Total cost
        """
        print("\n" + "="*80)
        print("SCANIA COST FUNCTION ANALYSIS")
        print("="*80)
        
        # Simple binary cost function (approximation)
        # Cost_FN = 300 (average of 200-500)
        # Cost_FP = 8 (average of 7-10)
        
        cm = confusion_matrix(y_test, y_pred)
        tn, fp, fn, tp = cm.ravel()
        
        cost_fn = 300  # Missing a failure
        cost_fp = 8    # Unnecessary check
        
        total_cost = (fn * cost_fn) + (fp * cost_fp)
        
        print(f"\n💰 Cost Analysis:")
        print(f"  False Negatives: {fn:4d} × ${cost_fn} = ${fn * cost_fn:,}")
        print(f"  False Positives: {fp:4d} × ${cost_fp}  = ${fp * cost_fp:,}")
        print(f"  {'─'*50}")
        print(f"  Total Cost:                    ${total_cost:,}")
        
        print(f"\n💡 Interpretation:")
        print(f"  • Each missed failure costs ~${cost_fn} (emergency repair, downtime)")
        print(f"  • Each false alarm costs ~${cost_fp} (unnecessary check)")
        print(f"  • Ratio: Missing failures is {cost_fn/cost_fp:.0f}x more expensive")
        
        return {
            'total_cost': total_cost,
            'fn_cost': fn * cost_fn,
            'fp_cost': fp * cost_fp,
            'false_negatives': fn,
            'false_positives': fp
        }
    
    def find_optimal_threshold(self, X_test, y_test, cost_fn=300, cost_fp=8):
        """
        Find optimal probability threshold based on cost function.
        
        Args:
            X_test: Test features
            y_test: Test labels
            cost_fn: Cost of false negative (missing failure)
            cost_fp: Cost of false positive (unnecessary check)
        
        Returns:
            Optimal threshold and costs
        """
        print("\n" + "="*80)
        print("OPTIMAL THRESHOLD ANALYSIS")
        print("="*80)
        
        y_pred_proba = self.predict_proba(X_test)
        
        # Try different thresholds
        thresholds = np.arange(0.1, 0.9, 0.05)
        costs = []
        
        for threshold in thresholds:
            y_pred_thresh = (y_pred_proba >= threshold).astype(int)
            cm = confusion_matrix(y_test, y_pred_thresh)
            tn, fp, fn, tp = cm.ravel()
            
            cost = (fn * cost_fn) + (fp * cost_fp)
            costs.append(cost)
        
        # Find optimal
        optimal_idx = np.argmin(costs)
        optimal_threshold = thresholds[optimal_idx]
        optimal_cost = costs[optimal_idx]
        
        print(f"\n🎯 Optimal Threshold Analysis:")
        print(f"  Cost of false negative: ${cost_fn}")
        print(f"  Cost of false positive: ${cost_fp}")
        print(f"  Optimal threshold: {optimal_threshold:.2f}")
        print(f"  Minimum cost: ${optimal_cost:,}")
        
        # Show comparison
        default_pred = (y_pred_proba >= 0.5).astype(int)
        cm_default = confusion_matrix(y_test, default_pred)
        _, fp_default, fn_default, _ = cm_default.ravel()
        default_cost = (fn_default * cost_fn) + (fp_default * cost_fp)
        
        print(f"\n📊 Comparison with default (0.5) threshold:")
        print(f"  Default cost: ${default_cost:,}")
        print(f"  Optimal cost: ${optimal_cost:,}")
        print(f"  Savings: ${default_cost - optimal_cost:,} ({(default_cost - optimal_cost)/default_cost*100:.1f}%)")
        
        return {
            'optimal_threshold': optimal_threshold,
            'optimal_cost': optimal_cost,
            'default_cost': default_cost,
            'savings': default_cost - optimal_cost,
            'thresholds': thresholds,
            'costs': costs
        }


if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║                      RISK PREDICTOR - DEMO                                   ║
    ║                                                                              ║
    ║  Focused module for failure risk prediction with:                           ║
    ║  • XGBoost with imbalance handling                                          ║
    ║  • Cost-sensitive learning (SCANIA cost function)                           ║
    ║  • Probability calibration                                                  ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    
    USAGE EXAMPLE:
    ==============
    
    from risk_predictor import RiskPredictor
    from scania_loader import load_scania_data, prepare_scania_for_classification
    from sklearn.model_selection import train_test_split
    
    # Load data
    data = load_scania_data()
    X, y, vehicle_ids = prepare_scania_for_classification(data)
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Train predictor
    predictor = RiskPredictor(handle_imbalance=True, calibrate_probabilities=True)
    predictor.train(X_train, y_train)
    
    # Evaluate
    results = predictor.evaluate(X_test, y_test)
    
    # Calculate costs
    cost_analysis = predictor.calculate_scania_cost(y_test, results['y_pred'])
    
    # Find optimal threshold
    threshold_analysis = predictor.find_optimal_threshold(X_test, y_test)
    
    ══════════════════════════════════════════════════════════════════════════════
    
    KEY FEATURES:
    • Handles 9:1 class imbalance automatically
    • Cost-sensitive evaluation (false negatives cost 37x more)
    • Probability calibration for reliable risk scores
    • Optimal threshold finding to minimize costs
    
    Perfect for Army XEM: Reliable risk predictions + explainability
    """)
