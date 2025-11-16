#!/usr/bin/env python3
"""
Feature Importance Analyzer
============================
Analyzes feature importance to identify the most predictive features for failure prediction.

This script:
1. Trains a model on ALL available features
2. Extracts feature importance scores
3. Identifies top N most important features
4. Retrains with reduced feature set
5. Compares performance metrics

Author: Predictive Maintenance System
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import xgboost as xgb
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import json
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")


class FeatureImportanceAnalyzer:
    """
    Analyzes and compares model performance with different feature sets.
    """
    
    def __init__(self):
        """Initialize the analyzer."""
        self.full_model = None
        self.reduced_model = None
        self.feature_importance_df = None
        self.top_features = None
        self.comparison_results = {}
        
        print("="*80)
        print("FEATURE IMPORTANCE ANALYZER INITIALIZED")
        print("="*80)
    
    def train_full_model(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_test: pd.DataFrame,
        y_test: pd.Series,
        **xgb_params
    ) -> Dict:
        """
        Train model on ALL available features.
        
        Args:
            X_train: Training features (all features)
            y_train: Training labels
            X_test: Test features
            y_test: Test labels
            **xgb_params: XGBoost parameters
        
        Returns:
            Performance metrics dictionary
        """
        print("\n" + "="*80)
        print("STEP 1: TRAINING MODEL ON ALL FEATURES")
        print("="*80)
        
        print(f"Total features: {X_train.shape[1]}")
        print(f"Training samples: {len(X_train)}")
        print(f"Class distribution:")
        print(f"  - Negative (healthy): {(y_train == 0).sum()} ({(y_train == 0).sum()/len(y_train)*100:.1f}%)")
        print(f"  - Positive (failed): {(y_train == 1).sum()} ({(y_train == 1).sum()/len(y_train)*100:.1f}%)")
        
        # Calculate scale_pos_weight
        scale_pos_weight = (len(y_train) - y_train.sum()) / y_train.sum()
        print(f"  - Imbalance ratio: {scale_pos_weight:.2f}:1")
        
        # Default XGBoost parameters
        default_params = {
            'n_estimators': 100,
            'max_depth': 6,
            'learning_rate': 0.1,
            'random_state': 42,
            'eval_metric': 'logloss',
            'use_label_encoder': False,
            'scale_pos_weight': scale_pos_weight,
            'n_jobs': -1
        }
        default_params.update(xgb_params)
        
        print(f"\nTraining XGBoost with parameters:")
        for key, value in default_params.items():
            print(f"  {key}: {value}")
        
        # Train model
        self.full_model = xgb.XGBClassifier(**default_params)
        self.full_model.fit(X_train, y_train)
        
        print("\n✓ Model trained successfully")
        
        # Evaluate
        results = self._evaluate_model(
            self.full_model,
            X_test,
            y_test,
            model_name="Full Model (All Features)"
        )
        
        self.comparison_results['full_model'] = results
        
        return results
    
    def extract_feature_importance(
        self,
        method: str = 'gain',
        top_n: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Extract and rank feature importance scores.
        
        Args:
            method: Importance type ('gain', 'weight', 'cover')
            top_n: Number of top features to return (None = all)
        
        Returns:
            DataFrame with feature importance rankings
        """
        print("\n" + "="*80)
        print("STEP 2: EXTRACTING FEATURE IMPORTANCE")
        print("="*80)
        
        if self.full_model is None:
            raise ValueError("Model not trained. Call train_full_model() first.")
        
        print(f"Importance method: {method}")
        
        # Get importance scores
        importance_dict = self.full_model.get_booster().get_score(importance_type=method)
        
        # Convert to DataFrame
        self.feature_importance_df = pd.DataFrame([
            {'feature': k, 'importance': v}
            for k, v in importance_dict.items()
        ]).sort_values('importance', ascending=False)
        
        # Add rank
        self.feature_importance_df['rank'] = range(1, len(self.feature_importance_df) + 1)
        
        # Add cumulative importance percentage
        total_importance = self.feature_importance_df['importance'].sum()
        self.feature_importance_df['importance_pct'] = (
            self.feature_importance_df['importance'] / total_importance * 100
        )
        self.feature_importance_df['cumulative_pct'] = (
            self.feature_importance_df['importance_pct'].cumsum()
        )
        
        print(f"\nTotal features with non-zero importance: {len(self.feature_importance_df)}")
        
        if top_n:
            result = self.feature_importance_df.head(top_n)
        else:
            result = self.feature_importance_df
        
        return result
    
    def select_top_features(self, n_features: int = 20) -> List[str]:
        """
        Select top N most important features.
        
        Args:
            n_features: Number of features to select
        
        Returns:
            List of top feature names
        """
        print("\n" + "="*80)
        print(f"STEP 3: SELECTING TOP {n_features} FEATURES")
        print("="*80)
        
        if self.feature_importance_df is None:
            raise ValueError("Feature importance not extracted. Call extract_feature_importance() first.")
        
        self.top_features = self.feature_importance_df.head(n_features)['feature'].tolist()
        
        print(f"\nTop {n_features} features selected:")
        for i, (_, row) in enumerate(self.feature_importance_df.head(n_features).iterrows(), 1):
            print(f"  {i:2d}. {row['feature']:<15} - Importance: {row['importance']:>8.1f} ({row['importance_pct']:>5.2f}%)")
        
        cumulative = self.feature_importance_df.head(n_features)['cumulative_pct'].iloc[-1]
        print(f"\n  These {n_features} features account for {cumulative:.1f}% of total importance")
        
        return self.top_features
    
    def train_reduced_model(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_test: pd.DataFrame,
        y_test: pd.Series,
        selected_features: Optional[List[str]] = None,
        **xgb_params
    ) -> Dict:
        """
        Train model on reduced feature set.
        
        Args:
            X_train: Training features (all features)
            y_train: Training labels
            X_test: Test features
            y_test: Test labels
            selected_features: List of features to use (None = use top_features)
            **xgb_params: XGBoost parameters
        
        Returns:
            Performance metrics dictionary
        """
        print("\n" + "="*80)
        print("STEP 4: TRAINING MODEL ON REDUCED FEATURE SET")
        print("="*80)
        
        if selected_features is None:
            if self.top_features is None:
                raise ValueError("No features selected. Call select_top_features() first.")
            selected_features = self.top_features
        
        print(f"Training with {len(selected_features)} selected features")
        
        # Filter to selected features
        X_train_reduced = X_train[selected_features]
        X_test_reduced = X_test[selected_features]
        
        # Calculate scale_pos_weight
        scale_pos_weight = (len(y_train) - y_train.sum()) / y_train.sum()
        
        # Default XGBoost parameters
        default_params = {
            'n_estimators': 100,
            'max_depth': 6,
            'learning_rate': 0.1,
            'random_state': 42,
            'eval_metric': 'logloss',
            'use_label_encoder': False,
            'scale_pos_weight': scale_pos_weight,
            'n_jobs': -1
        }
        default_params.update(xgb_params)
        
        # Train model
        self.reduced_model = xgb.XGBClassifier(**default_params)
        self.reduced_model.fit(X_train_reduced, y_train)
        
        print("\n✓ Reduced model trained successfully")
        
        # Evaluate
        results = self._evaluate_model(
            self.reduced_model,
            X_test_reduced,
            y_test,
            model_name=f"Reduced Model ({len(selected_features)} Features)"
        )
        
        self.comparison_results['reduced_model'] = results
        
        return results
    
    def _evaluate_model(
        self,
        model: xgb.XGBClassifier,
        X_test: pd.DataFrame,
        y_test: pd.Series,
        model_name: str = "Model"
    ) -> Dict:
        """
        Evaluate model performance.
        
        Args:
            model: Trained model
            X_test: Test features
            y_test: Test labels
            model_name: Name for display
        
        Returns:
            Performance metrics dictionary
        """
        print(f"\n{'='*80}")
        print(f"EVALUATING: {model_name}")
        print(f"{'='*80}")
        
        # Predictions
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)[:, 1]
        
        # Metrics
        accuracy = (y_pred == y_test).mean()
        
        # Handle edge case where all predictions are one class
        try:
            auc_score = roc_auc_score(y_test, y_pred_proba)
        except:
            auc_score = 0.0
            print("⚠️ Warning: Could not calculate AUC-ROC (single class predicted)")
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        tn, fp, fn, tp = cm.ravel()
        
        # Calculate rates
        if (tp + fn) > 0:
            recall = tp / (tp + fn)
        else:
            recall = 0
        
        if (tp + fp) > 0:
            precision = tp / (tp + fp)
        else:
            precision = 0
        
        if (tn + fp) > 0:
            specificity = tn / (tn + fp)
        else:
            specificity = 0
        
        # F1 score
        if precision + recall > 0:
            f1_score = 2 * (precision * recall) / (precision + recall)
        else:
            f1_score = 0
        
        print(f"\n📊 Metrics:")
        print(f"  Accuracy:    {accuracy:.4f}")
        print(f"  AUC-ROC:     {auc_score:.4f}")
        print(f"  Recall:      {recall:.4f} - Catches {recall*100:.1f}% of failures")
        print(f"  Precision:   {precision:.4f} - {precision*100:.1f}% of alerts are correct")
        print(f"  Specificity: {specificity:.4f}")
        print(f"  F1-Score:    {f1_score:.4f}")
        
        print(f"\n🎯 Confusion Matrix:")
        print(f"  True Negatives:  {tn:5d}")
        print(f"  False Positives: {fp:5d}")
        print(f"  False Negatives: {fn:5d} ⚠️")
        print(f"  True Positives:  {tp:5d}")
        
        # Cost analysis
        cost_fn = 300
        cost_fp = 8
        total_cost = (fn * cost_fn) + (fp * cost_fp)
        
        print(f"\n💰 Cost Analysis:")
        print(f"  False Negatives: {fn} × ${cost_fn} = ${fn * cost_fn:,}")
        print(f"  False Positives: {fp} × ${cost_fp}  = ${fp * cost_fp:,}")
        print(f"  Total Cost:                  ${total_cost:,}")
        
        return {
            'accuracy': accuracy,
            'auc_roc': auc_score,
            'recall': recall,
            'precision': precision,
            'specificity': specificity,
            'f1_score': f1_score,
            'confusion_matrix': cm,
            'true_negatives': int(tn),
            'false_positives': int(fp),
            'false_negatives': int(fn),
            'true_positives': int(tp),
            'total_cost': total_cost,
            'model_name': model_name
        }
    
    def compare_models(self) -> pd.DataFrame:
        """
        Compare performance of full vs reduced model.
        
        Returns:
            DataFrame with side-by-side comparison
        """
        print("\n" + "="*80)
        print("STEP 5: MODEL COMPARISON")
        print("="*80)
        
        if not self.comparison_results:
            raise ValueError("No models to compare. Train models first.")
        
        # Build comparison DataFrame
        metrics = ['accuracy', 'auc_roc', 'recall', 'precision', 'f1_score', 
                   'false_negatives', 'false_positives', 'total_cost']
        
        comparison_data = {}
        for model_key, results in self.comparison_results.items():
            comparison_data[results['model_name']] = {
                metric: results.get(metric, 0) for metric in metrics
            }
        
        comparison_df = pd.DataFrame(comparison_data).T
        
        print("\n📊 Performance Comparison:")
        print(comparison_df.to_string())
        
        # Calculate differences
        if len(self.comparison_results) == 2:
            print("\n📈 Difference (Reduced - Full):")
            full_results = self.comparison_results['full_model']
            reduced_results = self.comparison_results['reduced_model']
            
            for metric in ['accuracy', 'auc_roc', 'recall', 'precision', 'f1_score']:
                diff = reduced_results[metric] - full_results[metric]
                pct_change = (diff / full_results[metric] * 100) if full_results[metric] > 0 else 0
                symbol = "📈" if diff > 0 else "📉" if diff < 0 else "➡️"
                print(f"  {metric.capitalize():<15}: {diff:+.4f} ({pct_change:+.1f}%) {symbol}")
            
            cost_diff = reduced_results['total_cost'] - full_results['total_cost']
            cost_symbol = "💰" if cost_diff < 0 else "💸" if cost_diff > 0 else "➡️"
            print(f"  {'Total Cost':<15}: ${cost_diff:+,.0f} {cost_symbol}")
        
        return comparison_df
    
    def save_results(self, output_dir: str = "data/analysis"):
        """
        Save analysis results to files.
        
        Args:
            output_dir: Directory to save results
        """
        print("\n" + "="*80)
        print("SAVING ANALYSIS RESULTS")
        print("="*80)
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save feature importance
        if self.feature_importance_df is not None:
            importance_file = output_path / f"feature_importance_{timestamp}.csv"
            self.feature_importance_df.to_csv(importance_file, index=False)
            print(f"✓ Feature importance saved: {importance_file}")
        
        # Save top features
        if self.top_features is not None:
            top_features_file = output_path / f"top_features_{timestamp}.json"
            with open(top_features_file, 'w') as f:
                json.dump({
                    'top_features': self.top_features,
                    'n_features': len(self.top_features),
                    'timestamp': datetime.now().isoformat()
                }, f, indent=2)
            print(f"✓ Top features saved: {top_features_file}")
        
        # Save comparison results
        if self.comparison_results:
            comparison_file = output_path / f"model_comparison_{timestamp}.json"
            
            # Convert numpy types to Python types for JSON serialization
            serializable_results = {}
            for key, results in self.comparison_results.items():
                serializable_results[key] = {
                    k: float(v) if isinstance(v, (np.integer, np.floating)) else v
                    for k, v in results.items()
                    if k != 'confusion_matrix'  # Skip confusion matrix (numpy array)
                }
            
            with open(comparison_file, 'w') as f:
                json.dump(serializable_results, f, indent=2)
            print(f"✓ Comparison results saved: {comparison_file}")
        
        print(f"\n✓ All results saved to: {output_path}")
    
    def plot_feature_importance(
        self,
        top_n: int = 20,
        output_dir: Optional[str] = None
    ):
        """
        Plot feature importance chart.
        
        Args:
            top_n: Number of top features to plot
            output_dir: Directory to save plot (None = display only)
        """
        if self.feature_importance_df is None:
            raise ValueError("Feature importance not extracted.")
        
        plt.figure(figsize=(12, 8))
        
        top_features_df = self.feature_importance_df.head(top_n)
        
        # Plot
        plt.barh(range(top_n), top_features_df['importance'][::-1])
        plt.yticks(range(top_n), top_features_df['feature'][::-1])
        plt.xlabel('Importance Score', fontsize=12)
        plt.ylabel('Feature', fontsize=12)
        plt.title(f'Top {top_n} Most Important Features', fontsize=14, fontweight='bold')
        plt.grid(axis='x', alpha=0.3)
        plt.tight_layout()
        
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            plot_file = output_path / f"feature_importance_plot_{timestamp}.png"
            plt.savefig(plot_file, dpi=300, bbox_inches='tight')
            print(f"✓ Plot saved: {plot_file}")
        else:
            plt.show()
        
        plt.close()


def run_full_analysis(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    n_top_features: int = 20,
    save_results: bool = True,
    output_dir: str = "data/analysis"
) -> Dict:
    """
    Run complete feature importance analysis.
    
    Args:
        X_train: Training features
        y_train: Training labels
        X_test: Test features
        y_test: Test labels
        n_top_features: Number of top features to select
        save_results: Whether to save results to files
        output_dir: Directory for saving results
    
    Returns:
        Dictionary with all analysis results
    """
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + "FEATURE IMPORTANCE ANALYSIS".center(78) + "║")
    print("╚" + "="*78 + "╝\n")
    
    # Initialize analyzer
    analyzer = FeatureImportanceAnalyzer()
    
    # Step 1: Train on all features
    full_results = analyzer.train_full_model(X_train, y_train, X_test, y_test)
    
    # Step 2: Extract feature importance
    importance_df = analyzer.extract_feature_importance(method='gain')
    
    # Step 3: Select top features
    top_features = analyzer.select_top_features(n_features=n_top_features)
    
    # Step 4: Train on reduced features
    reduced_results = analyzer.train_reduced_model(X_train, y_train, X_test, y_test)
    
    # Step 5: Compare models
    comparison_df = analyzer.compare_models()
    
    # Save results
    if save_results:
        analyzer.save_results(output_dir=output_dir)
        analyzer.plot_feature_importance(top_n=n_top_features, output_dir=output_dir)
    
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + "ANALYSIS COMPLETED SUCCESSFULLY".center(78) + "║")
    print("╚" + "="*78 + "╝\n")
    
    return {
        'analyzer': analyzer,
        'full_results': full_results,
        'reduced_results': reduced_results,
        'importance_df': importance_df,
        'top_features': top_features,
        'comparison_df': comparison_df
    }


if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║              FEATURE IMPORTANCE ANALYZER - DEMO                              ║
    ║                                                                              ║
    ║  Identifies most predictive features:                                       ║
    ║  • Train on ALL features                                                    ║
    ║  • Extract importance scores                                                ║
    ║  • Select top N features                                                    ║
    ║  • Retrain with reduced set                                                 ║
    ║  • Compare performance                                                      ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    
    USAGE EXAMPLE:
    ==============
    
    from core.feature_importance_analyzer import run_full_analysis
    from core.scania_loader import load_scania_data, prepare_scania_for_classification
    from sklearn.model_selection import train_test_split
    
    # Load data
    data = load_scania_data()
    X, y, vehicle_ids = prepare_scania_for_classification(data)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Run full analysis
    results = run_full_analysis(
        X_train, y_train,
        X_test, y_test,
        n_top_features=20,
        save_results=True
    )
    
    # Access results
    top_features = results['top_features']
    comparison = results['comparison_df']
    
    print(f"Top 20 features: {top_features}")
    print(comparison)
    
    ══════════════════════════════════════════════════════════════════════════════
    
    KEY OUTPUTS:
    • Feature importance rankings (CSV)
    • Top N feature list (JSON)
    • Model comparison metrics (JSON)
    • Feature importance plot (PNG)
    • Side-by-side performance comparison
    
    Perfect for: Determining which features to require from users
    """)
