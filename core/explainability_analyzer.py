#!/usr/bin/env python3
"""
Explainability Analyzer for Predictive Maintenance
===================================================
Explains WHY vehicles are predicted to fail - the core value-add for Army XEM.

This module provides explainability techniques to help commanders understand:
- Which features contribute most to failure risk
- Why a specific vehicle is high-risk
- What operational patterns increase failure rates
- How different vehicle cohorts compare

Author: Predictive Maintenance for Army XEM
Use Case: Answer "WHY will this vehicle fail?" not just "WHEN"
"""

import pandas as pd
import numpy as np
import warnings
from typing import Dict, List, Tuple, Optional

warnings.filterwarnings("ignore")


class ExplainabilityAnalyzer:
    """
    Analyzes and explains model predictions for predictive maintenance.
    
    This class provides multiple explainability techniques:
    1. SHAP values - Explain individual predictions
    2. Feature importance - Global view of what matters
    3. Risk factor analysis - Which features increase/decrease risk
    4. Cohort analysis - Compare groups (engine types, conditions, etc.)
    
    Perfect for military commanders who need actionable insights.
    """
    
    def __init__(self, model, X_train, y_train, X_test=None, feature_names=None):
        """
        Initialize the explainability analyzer.
        
        Args:
            model: Trained model (sklearn-compatible with predict_proba)
            X_train: Training features (DataFrame or array)
            y_train: Training labels
            X_test: Optional test features for evaluation
            feature_names: List of feature names (if X is array)
        """
        self.model = model
        self.X_train = X_train
        self.y_train = y_train
        self.X_test = X_test
        
        # Handle feature names
        if isinstance(X_train, pd.DataFrame):
            self.feature_names = X_train.columns.tolist()
            self.X_train_array = X_train.values
        else:
            self.feature_names = feature_names or [f"feature_{i}" for i in range(X_train.shape[1])]
            self.X_train_array = X_train
            
        self.shap_explainer = None
        self.shap_values = None
        
        print("="*80)
        print("EXPLAINABILITY ANALYZER INITIALIZED")
        print("="*80)
        print(f"Model type: {type(model).__name__}")
        print(f"Training samples: {len(X_train)}")
        print(f"Features: {len(self.feature_names)}")
        print(f"Feature names available: {len(self.feature_names)}")
        
    def get_feature_importance(self, top_n=20) -> pd.DataFrame:
        """
        Get global feature importance from the model.
        
        This shows what matters most across ALL predictions.
        For commanders: "Temperature variability is the #1 failure predictor"
        
        Args:
            top_n: Number of top features to return
            
        Returns:
            DataFrame with features and importance scores
        """
        print("\n" + "="*80)
        print("FEATURE IMPORTANCE ANALYSIS")
        print("="*80)
        print("Question: What features matter most for predicting failures?")
        print("Use case: Help commanders understand fleet-wide risk drivers")
        
        # Try to get feature importance from model
        importance_scores = None
        
        if hasattr(self.model, 'feature_importances_'):
            # Tree-based models (Random Forest, XGBoost, etc.)
            importance_scores = self.model.feature_importances_
            method = "Tree-based importance"
        elif hasattr(self.model, 'coef_'):
            # Linear models (Logistic Regression, etc.)
            importance_scores = np.abs(self.model.coef_[0])
            method = "Coefficient magnitude"
        else:
            print("⚠ Model doesn't have built-in feature importance")
            print("  Use SHAP values for model-agnostic importance")
            return None
            
        # Create DataFrame
        importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': importance_scores
        }).sort_values('importance', ascending=False)
        
        # Normalize to percentages
        importance_df['importance_pct'] = (
            importance_df['importance'] / importance_df['importance'].sum() * 100
        )
        
        print(f"\n✓ Feature importance calculated using: {method}")
        print(f"\nTop {top_n} Most Important Features:")
        print("-"*80)
        
        for idx, row in importance_df.head(top_n).iterrows():
            print(f"  {row['feature']:40s} | {row['importance']:.4f} ({row['importance_pct']:.1f}%)")
        
        print("\nInterpretation for Commanders:")
        top_feature = importance_df.iloc[0]
        print(f"  → '{top_feature['feature']}' is the strongest failure predictor")
        print(f"  → It accounts for {top_feature['importance_pct']:.1f}% of the model's decision-making")
        print(f"  → Focus monitoring and maintenance efforts on top 5-10 features")
        
        return importance_df
    
    def initialize_shap(self, background_samples=100):
        """
        Initialize SHAP explainer for detailed predictions.
        
        SHAP (SHapley Additive exPlanations) is the gold standard for
        explaining individual predictions.
        
        Args:
            background_samples: Number of training samples to use as background
                               (smaller = faster, larger = more accurate)
        """
        try:
            import shap
            
            print("\n" + "="*80)
            print("INITIALIZING SHAP EXPLAINER")
            print("="*80)
            print("SHAP will explain WHY each specific vehicle is high/low risk")
            print(f"Using {background_samples} background samples for baseline")
            
            # Select background data (sample from training set)
            if len(self.X_train_array) > background_samples:
                background_indices = np.random.choice(
                    len(self.X_train_array), 
                    size=background_samples, 
                    replace=False
                )
                background_data = self.X_train_array[background_indices]
            else:
                background_data = self.X_train_array
            
            # Create SHAP explainer
            # TreeExplainer for tree-based models (fast and exact)
            # KernelExplainer for any model (slower but model-agnostic)
            
            model_type = type(self.model).__name__
            
            if any(x in model_type.lower() for x in ['forest', 'tree', 'xgb', 'boost', 'gradient']):
                print(f"✓ Using TreeExplainer (fast, exact) for {model_type}")
                self.shap_explainer = shap.TreeExplainer(self.model)
            else:
                print(f"✓ Using KernelExplainer (model-agnostic) for {model_type}")
                def model_predict(X):
                    return self.model.predict_proba(X)[:, 1]
                self.shap_explainer = shap.KernelExplainer(model_predict, background_data)
            
            print("✓ SHAP explainer ready")
            print("\nNext: Call explain_prediction() for individual vehicle analysis")
            
        except ImportError:
            print("✗ SHAP library not installed")
            print("  Install with: pip install shap")
            self.shap_explainer = None
            
    def explain_prediction(self, X_instance, instance_id=None, top_n=10) -> Dict:
        """
        Explain why a specific vehicle is predicted to fail (or not).
        
        This is THE KEY FUNCTION for Army XEM commanders.
        
        Args:
            X_instance: Single instance to explain (array or DataFrame row)
            instance_id: Optional ID for this instance (e.g., vehicle ID)
            top_n: Number of top contributing features to show
            
        Returns:
            Dictionary with explanation details
        """
        if self.shap_explainer is None:
            print("⚠ SHAP explainer not initialized. Call initialize_shap() first.")
            return None
        
        import shap
        
        # Convert to array if needed
        if isinstance(X_instance, pd.Series):
            X_array = X_instance.values.reshape(1, -1)
        elif isinstance(X_instance, pd.DataFrame):
            X_array = X_instance.values
        else:
            X_array = np.array(X_instance).reshape(1, -1)
        
        # Get prediction
        prediction_proba = self.model.predict_proba(X_array)[0, 1]
        prediction_class = int(prediction_proba >= 0.5)
        
        # Calculate SHAP values
        shap_values = self.shap_explainer.shap_values(X_array)
        
        # Handle different SHAP output formats
        if isinstance(shap_values, list):
            # Binary classification - get positive class
            shap_values = shap_values[1]
        
        # Get base value (expected value)
        if hasattr(self.shap_explainer, 'expected_value'):
            base_value = self.shap_explainer.expected_value
            if isinstance(base_value, (list, np.ndarray)):
                base_value = base_value[1] if len(base_value) > 1 else base_value[0]
        else:
            base_value = 0.0
        
        # Flatten SHAP values to 1D for single instance
        if len(shap_values.shape) > 1:
            shap_values_1d = shap_values[0]  # Get first (only) instance
        else:
            shap_values_1d = shap_values
        
        # Ensure it's really 1D
        shap_values_1d = np.asarray(shap_values_1d).flatten()
        
        # Flatten X_array to 1D
        X_array_1d = np.asarray(X_array).flatten()
        
        # Debug: Check lengths match
        if len(self.feature_names) != len(shap_values_1d) or len(self.feature_names) != len(X_array_1d):
            print(f"DEBUG: Length mismatch!")
            print(f"  feature_names: {len(self.feature_names)}")
            print(f"  shap_values_1d: {len(shap_values_1d)}, shape: {shap_values_1d.shape}")
            print(f"  X_array_1d: {len(X_array_1d)}, shape: {X_array_1d.shape}")
            print(f"  X_array original shape: {X_array.shape}")
            # Take only the first n_features elements
            shap_values_1d = shap_values_1d[:len(self.feature_names)]
            X_array_1d = X_array_1d[:len(self.feature_names)]
        
        # Create explanation DataFrame - ensure all arrays are 1D and same length
        shap_df = pd.DataFrame({
            'feature': self.feature_names,
            'value': X_array_1d,
            'shap_value': shap_values_1d,
            'abs_shap': np.abs(shap_values_1d)
        }).sort_values('abs_shap', ascending=False)
        
        # Print explanation
        print("\n" + "="*80)
        print(f"PREDICTION EXPLANATION: {instance_id or 'Vehicle'}")
        print("="*80)
        
        risk_level = "HIGH RISK" if prediction_proba >= 0.7 else "MEDIUM RISK" if prediction_proba >= 0.4 else "LOW RISK"
        print(f"\n🎯 PREDICTION: {risk_level}")
        print(f"   Failure Probability: {prediction_proba:.1%}")
        print(f"   Classification: {'WILL FAIL' if prediction_class == 1 else 'WILL NOT FAIL'}")
        
        print(f"\n📊 TOP {top_n} CONTRIBUTING FACTORS:")
        print("-"*80)
        print(f"{'Feature':<40} {'Value':>12} {'Impact':>12} {'Effect':>12}")
        print("-"*80)
        
        for idx, row in shap_df.head(top_n).iterrows():
            effect = "🔴 INCREASES" if row['shap_value'] > 0 else "🟢 DECREASES"
            print(f"{row['feature']:<40} {row['value']:>12.3f} {row['shap_value']:>12.4f} {effect:>12}")
        
        # Commander-friendly summary
        print("\n📋 COMMANDER SUMMARY:")
        top_risk = shap_df.iloc[0]
        if top_risk['shap_value'] > 0:
            print(f"  → Primary risk driver: {top_risk['feature']}")
            print(f"  → This feature contributes +{top_risk['shap_value']:.3f} to failure risk")
        else:
            print(f"  → Primary protective factor: {top_risk['feature']}")
            print(f"  → This feature reduces failure risk by {abs(top_risk['shap_value']):.3f}")
        
        # Count positive vs negative factors
        risk_increasing = (shap_df['shap_value'] > 0).sum()
        risk_decreasing = (shap_df['shap_value'] < 0).sum()
        print(f"  → {risk_increasing} factors increase risk, {risk_decreasing} factors decrease risk")
        
        # Return structured data
        return {
            'instance_id': instance_id,
            'prediction_proba': prediction_proba,
            'prediction_class': prediction_class,
            'risk_level': risk_level,
            'base_value': base_value,
            'shap_values': shap_values,
            'shap_df': shap_df,
            'top_factors': shap_df.head(top_n).to_dict('records')
        }
    
    def get_shap_summary(self, X_data=None, max_display=20):
        """
        Get SHAP summary across multiple predictions.
        
        Shows what features matter most on average (global importance via SHAP).
        
        Args:
            X_data: Data to explain (uses X_test if not provided)
            max_display: Max features to display
        """
        if self.shap_explainer is None:
            print("⚠ SHAP explainer not initialized. Call initialize_shap() first.")
            return None
            
        import shap
        
        if X_data is None:
            X_data = self.X_test if self.X_test is not None else self.X_train_array[:1000]
        elif isinstance(X_data, pd.DataFrame):
            X_data = X_data.values
            
        print("\n" + "="*80)
        print("SHAP SUMMARY - GLOBAL FEATURE IMPORTANCE")
        print("="*80)
        print(f"Analyzing {len(X_data)} samples to determine feature importance")
        
        # Calculate SHAP values
        shap_values = self.shap_explainer.shap_values(X_data)
        
        if isinstance(shap_values, list):
            shap_values = shap_values[1]  # Positive class for binary
        
        # Calculate mean absolute SHAP values
        mean_abs_shap = np.abs(shap_values).mean(axis=0)
        
        # Ensure it's 1D
        mean_abs_shap = np.asarray(mean_abs_shap).flatten()
        
        # Handle cases where mean_abs_shap has wrong shape (2x features for binary classification)
        if len(mean_abs_shap) != len(self.feature_names):
            print(f"DEBUG: SHAP summary length mismatch")
            print(f"  feature_names: {len(self.feature_names)}")
            print(f"  mean_abs_shap: {len(mean_abs_shap)}, shape: {mean_abs_shap.shape}")
            # Take only first n_features
            mean_abs_shap = mean_abs_shap[:len(self.feature_names)]
        
        shap_importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'mean_abs_shap': mean_abs_shap
        }).sort_values('mean_abs_shap', ascending=False)
        
        print(f"\nTop {max_display} Most Important Features (by SHAP):")
        print("-"*80)
        
        for idx, row in shap_importance_df.head(max_display).iterrows():
            print(f"  {row['feature']:40s} | Mean |SHAP|: {row['mean_abs_shap']:.4f}")
        
        self.shap_values = shap_values  # Store for potential plotting
        
        return shap_importance_df


# Simple demonstration
if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║                    EXPLAINABILITY ANALYZER - DEMO                            ║
    ║              Answer "WHY" vehicles will fail, not just "WHEN"                ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    
    This module provides explainability for predictive maintenance models.
    
    USAGE EXAMPLE:
    ==============
    
    from explainability_analyzer import ExplainabilityAnalyzer
    from sklearn.ensemble import RandomForestClassifier
    
    # 1. Train your model
    model = RandomForestClassifier()
    model.fit(X_train, y_train)
    
    # 2. Create explainability analyzer
    analyzer = ExplainabilityAnalyzer(model, X_train, y_train, X_test)
    
    # 3. Get global feature importance
    importance = analyzer.get_feature_importance(top_n=10)
    
    # 4. Initialize SHAP for detailed explanations
    analyzer.initialize_shap(background_samples=100)
    
    # 5. Explain a specific prediction
    explanation = analyzer.explain_prediction(X_test[0], instance_id="Vehicle_12345")
    
    # 6. Get SHAP summary across all test data
    shap_summary = analyzer.get_shap_summary(X_test)
    
    ══════════════════════════════════════════════════════════════════════════════
    
    KEY OUTPUTS FOR COMMANDERS:
    - Risk score (0-100%)
    - Top 5-10 risk factors
    - Why this specific vehicle is high/low risk
    - Which features to monitor fleet-wide
    
    Next step: Integrate with SCANIA dataset and trained models
    """)
