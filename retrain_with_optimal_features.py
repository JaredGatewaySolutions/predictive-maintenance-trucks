#!/usr/bin/env python3
"""
Retrain Model with Optimal Features
====================================
Retrains the production model using the scientifically-selected top 20 features
from the feature importance analysis.

This script:
1. Loads the full SCaNIa dataset
2. Uses only the top 20 most important features
3. Trains a production-ready model with proper hyperparameters
4. Saves the model with complete metadata
5. Compares against the current production model

Author: Predictive Maintenance System
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.scania_loader import load_scania_data, prepare_scania_for_classification
from core.pipeline import TrainingPipeline
from core.model_manager import ModelManager
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np


# ============================================================================
# OPTIMAL FEATURES (From Full Dataset Analysis - Nov 15, 2025)
# ============================================================================

OPTIMAL_TOP_20_FEATURES = [
    "158_9",   # Rank 1 - 3.41% importance
    "167_6",   # Rank 2 - 1.88%
    "167_3",   # Rank 3 - 1.77%
    "158_5",   # Rank 4 - 1.71%
    "291_4",   # Rank 5 - 1.48%
    "459_3",   # Rank 6 - 1.34%
    "459_15",  # Rank 7 - 1.29%
    "459_8",   # Rank 8 - 1.27%
    "167_1",   # Rank 9 - 1.26%
    "459_14",  # Rank 10 - 1.26%
    "272_0",   # Rank 11 - 1.25%
    "397_33",  # Rank 12 - 1.23%
    "291_1",   # Rank 13 - 1.22%
    "397_0",   # Rank 14 - 1.22%
    "291_5",   # Rank 15 - 1.21%
    "272_2",   # Rank 16 - 1.18%
    "459_9",   # Rank 17 - 1.17%
    "158_6",   # Rank 18 - 1.17%
    "397_3",   # Rank 19 - 1.15%
    "272_4"    # Rank 20 - 1.12%
]

# Performance from analysis (Full Dataset):
# - Recall: 55.5% (catches 55.5% of failures)
# - Accuracy: 75.9%
# - AUC-ROC: 0.746
# - Cost: $68,048 (saved $8,308 vs full feature model!)
# - 81% fewer features (20 vs 105)


def print_banner(text):
    """Print a formatted banner."""
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + text.center(78) + "║")
    print("╚" + "="*78 + "╝\n")


def load_and_prepare_data(data_dir='data/raw', test_size=0.2):
    """
    Load and prepare data with optimal features only.
    
    Args:
        data_dir: Directory containing SCaNIa data
        test_size: Test set proportion
    
    Returns:
        Dictionary with data splits
    """
    print_banner("LOADING DATA WITH OPTIMAL FEATURES")
    
    print("📊 Loading SCaNIa dataset...")
    data = load_scania_data(data_dir=data_dir)
    
    print("🔧 Preparing data for classification...")
    X_full, y, vehicle_ids = prepare_scania_for_classification(data)
    
    print(f"\n✓ Full dataset loaded:")
    print(f"  Total vehicles: {len(X_full):,}")
    print(f"  Total features available: {X_full.shape[1]}")
    print(f"  Failures: {y.sum():,} ({y.sum()/len(y)*100:.1f}%)")
    print(f"  Healthy: {(y == 0).sum():,} ({(y == 0).sum()/len(y)*100:.1f}%)")
    
    # Filter to optimal features only
    print(f"\n🎯 Filtering to top {len(OPTIMAL_TOP_20_FEATURES)} optimal features...")
    
    # Check which features are available
    missing_features = [f for f in OPTIMAL_TOP_20_FEATURES if f not in X_full.columns]
    if missing_features:
        print(f"⚠️  Warning: {len(missing_features)} features not found in dataset:")
        for feat in missing_features:
            print(f"    - {feat}")
    
    available_features = [f for f in OPTIMAL_TOP_20_FEATURES if f in X_full.columns]
    print(f"✓ Using {len(available_features)} features")
    
    X = X_full[available_features].copy()
    
    # Train/test split
    print(f"\n📂 Splitting data (test_size={test_size})...")
    X_train, X_test, y_train, y_test, ids_train, ids_test = train_test_split(
        X, y, vehicle_ids,
        test_size=test_size,
        random_state=42,
        stratify=y
    )
    
    print(f"✓ Data split:")
    print(f"  Training: {len(X_train):,} vehicles ({len(X_train)/len(X)*100:.0f}%)")
    print(f"  Test: {len(X_test):,} vehicles ({len(X_test)/len(X)*100:.0f}%)")
    print(f"  Training failures: {y_train.sum():,} ({y_train.sum()/len(y_train)*100:.1f}%)")
    print(f"  Test failures: {y_test.sum():,} ({y_test.sum()/len(y_test)*100:.1f}%)")
    
    return {
        'X_train': X_train,
        'X_test': X_test,
        'y_train': y_train,
        'y_test': y_test,
        'ids_train': ids_train,
        'ids_test': ids_test,
        'feature_names': available_features
    }


def train_optimal_model(data_splits, save_model=True):
    """
    Train model with optimal features.
    
    Args:
        data_splits: Dictionary with train/test splits
        save_model: Whether to save the trained model
    
    Returns:
        Trained pipeline and results
    """
    print_banner("TRAINING MODEL WITH OPTIMAL FEATURES")
    
    # Initialize pipeline
    pipeline = TrainingPipeline(
        data_dir='data/raw',
        models_dir='data/models',
        handle_imbalance=True,
        calibrate_probabilities=True
    )
    
    # Train model
    print("🚀 Training XGBoost model...")
    predictor = pipeline.train_model(
        data_splits['X_train'],
        data_splits['y_train'],
        n_estimators=150,  # Increased for better performance
        max_depth=7,       # Slightly deeper trees
        learning_rate=0.08,
        random_state=42
    )
    
    # Evaluate
    print_banner("EVALUATING MODEL PERFORMANCE")
    evaluation = pipeline.evaluate_model(
        data_splits['X_test'],
        data_splits['y_test']
    )
    
    # Save model
    version = None
    if save_model:
        print_banner("SAVING MODEL")
        
        metadata = {
            "model_type": "RiskPredictor_OptimalFeatures",
            "feature_selection_method": "XGBoost Feature Importance (Full Dataset)",
            "feature_selection_date": "2025-11-15",
            "n_features": len(data_splits['feature_names']),
            "features": data_splits['feature_names'],
            "training_samples": len(data_splits['X_train']),
            "test_samples": len(data_splits['X_test']),
            "metrics": {
                "accuracy": float(evaluation['eval_results']['accuracy']),
                "auc_roc": float(evaluation['eval_results']['auc_roc']),
                "recall": float(evaluation['eval_results']['recall']),
                "precision": float(evaluation['eval_results']['precision']),
                "specificity": float(evaluation['eval_results']['specificity']),
                "f1_score": float(evaluation['eval_results']['recall'] * evaluation['eval_results']['precision'] * 2 / 
                                  (evaluation['eval_results']['recall'] + evaluation['eval_results']['precision']) 
                                  if (evaluation['eval_results']['recall'] + evaluation['eval_results']['precision']) > 0 else 0)
            },
            "cost_analysis": {
                "total_cost": float(evaluation['cost_results']['total_cost']),
                "false_negatives": int(evaluation['cost_results']['false_negatives']),
                "false_positives": int(evaluation['cost_results']['false_positives'])
            },
            "optimal_threshold": float(evaluation['threshold_results']['optimal_threshold']),
            "cost_savings_vs_default": float(evaluation['threshold_results']['savings']),
            "handle_imbalance": True,
            "calibrate_probabilities": True,
            "training_date": datetime.now().isoformat()
        }
        
        # Sample training data for SHAP
        sample_size = min(100, len(data_splits['X_train']))
        sample_indices = np.random.choice(len(data_splits['X_train']), size=sample_size, replace=False)
        X_train_sample = data_splits['X_train'].iloc[sample_indices]
        y_train_sample = data_splits['y_train'].iloc[sample_indices]
        
        version = pipeline.save_model(
            metadata=metadata,
            X_train_sample=X_train_sample,
            y_train_sample=y_train_sample
        )
        
        print(f"\n✅ Model saved as version: {version}")
    
    return {
        'pipeline': pipeline,
        'predictor': predictor,
        'evaluation': evaluation,
        'version': version
    }


def compare_with_current_model(new_results, current_model_path='data/models/current/metadata.json'):
    """
    Compare new model with current production model.
    
    Args:
        new_results: Results from new model
        current_model_path: Path to current model metadata
    """
    print_banner("COMPARING WITH CURRENT PRODUCTION MODEL")
    
    try:
        with open(current_model_path, 'r') as f:
            current_metadata = json.load(f)
        
        current_metrics = current_metadata.get('metrics', {})
        new_metrics = new_results['evaluation']['eval_results']
        
        print("📊 Performance Comparison:\n")
        print(f"{'Metric':<20} {'Current Model':<20} {'New Model':<20} {'Change':<20}")
        print("-" * 80)
        
        metrics_to_compare = [
            ('Accuracy', 'accuracy'),
            ('AUC-ROC', 'auc_roc'),
            ('Recall', 'recall'),
            ('Precision', 'precision')
        ]
        
        for metric_name, metric_key in metrics_to_compare:
            current_val = current_metrics.get(metric_key, 0)
            new_val = new_metrics.get(metric_key, 0)
            diff = new_val - current_val
            
            if current_val > 0:
                pct_change = (diff / current_val) * 100
                symbol = "📈" if diff > 0 else "📉" if diff < 0 else "➡️"
                print(f"{metric_name:<20} {current_val:<20.4f} {new_val:<20.4f} {diff:+.4f} ({pct_change:+.1f}%) {symbol}")
            else:
                print(f"{metric_name:<20} {current_val:<20.4f} {new_val:<20.4f} {diff:+.4f}")
        
        print("\n" + "="*80)
        
        # Feature count comparison
        current_features = len(current_metadata.get('features', []))
        new_features = len(OPTIMAL_TOP_20_FEATURES)
        
        print(f"\n📋 Feature Count:")
        print(f"  Current model: {current_features} features")
        print(f"  New model: {new_features} features")
        print(f"  Reduction: {current_features - new_features} features ({(current_features - new_features)/current_features*100:.1f}%)")
        
        # Recommendation
        print("\n" + "="*80)
        print("💡 RECOMMENDATION:")
        
        if new_metrics['recall'] >= current_metrics.get('recall', 0):
            print("✅ New model has BETTER or EQUAL recall - Deploy it!")
            print(f"   • Catches {new_metrics['recall']*100:.1f}% of failures vs {current_metrics.get('recall', 0)*100:.1f}%")
            print(f"   • Uses {new_features} features instead of {current_features}")
            print(f"   • Much better user experience!")
        else:
            print("⚠️  New model has lower recall - Review tradeoffs carefully")
            print(f"   • Consider if the UX benefit is worth the recall drop")
        
    except FileNotFoundError:
        print(f"⚠️  Current model metadata not found at: {current_model_path}")
        print("   Cannot compare with current model")
    except Exception as e:
        print(f"❌ Error comparing models: {e}")


def main():
    """Main execution function."""
    
    print("╔" + "="*78 + "╗")
    print("║" + "RETRAIN MODEL WITH OPTIMAL FEATURES".center(78) + "║")
    print("║" + "Based on Full Dataset Feature Importance Analysis".center(78) + "║")
    print("╚" + "="*78 + "╝\n")
    
    print("📋 Configuration:")
    print(f"  Features: {len(OPTIMAL_TOP_20_FEATURES)} optimal features")
    print(f"  Expected Recall: ~55.5% (from analysis)")
    print(f"  Expected Accuracy: ~75.9%")
    print(f"  Expected Cost Savings: ~$8,300 vs full model")
    print(f"  Data Source: data/raw")
    
    try:
        # Step 1: Load data
        data_splits = load_and_prepare_data()
        
        # Step 2: Train model
        results = train_optimal_model(data_splits, save_model=True)
        
        # Step 3: Compare with current model
        compare_with_current_model(results)
        
        # Success summary
        print_banner("RETRAINING COMPLETED SUCCESSFULLY")
        
        print("✅ Summary:")
        print(f"   • Model trained on {len(data_splits['X_train']):,} vehicles")
        print(f"   • Using {len(data_splits['feature_names'])} optimal features")
        print(f"   • Recall: {results['evaluation']['eval_results']['recall']:.1%}")
        print(f"   • Accuracy: {results['evaluation']['eval_results']['accuracy']:.1%}")
        print(f"   • Model saved as: {results['version']}")
        print(f"\n📁 Next Steps:")
        print(f"   1. Review the model performance above")
        print(f"   2. Update feature_mapper.py with the new features")
        print(f"   3. Update API to accept these 20 features")
        print(f"   4. Test the model with real predictions")
        print(f"   5. Deploy to production")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error during retraining: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
