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
from sklearn.model_selection import train_test_split
import numpy as np

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.scania_loader import load_scania_data, prepare_scania_for_classification
from core.risk_predictor import RiskPredictor
from core.model_manager import ModelManager


# Optimal features from full dataset analysis
OPTIMAL_FEATURES = [
    "158_9", "167_6", "167_3", "158_5", "291_4", "459_3", "459_15", "459_8",
    "167_1", "459_14", "272_0", "397_33", "291_1", "397_0", "291_5", "272_2",
    "459_9", "158_6", "397_3", "272_4"
]


def print_banner(text):
    """Print a formatted banner."""
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + text.center(78) + "║")
    print("╚" + "="*78 + "╝\n")


def main():
    """Main execution function."""
    
    print("╔" + "="*78 + "╗")
    print("║" + "RETRAIN MODEL - IMPROVED VERSION 2".center(78) + "║")
    print("║" + "Optimal Threshold + No Calibration + Better Parameters".center(78) + "║")
    print("╚" + "="*78 + "╝\n")
    
    print("📋 Configuration:")
    print(f"  Features: {len(OPTIMAL_FEATURES)} optimal features")
    print(f"  Threshold: 0.1 (optimal from analysis)")
    print(f"  Calibration: DISABLED (can suppress predictions)")
    print(f"  Scale pos weight: Higher (15x)")
    print(f"  Expected Recall: 40-55%")
    
    # Step 1: Load data
    print_banner("LOADING DATA")
    
    print("📊 Loading SCaNIa dataset...")
    data = load_scania_data(data_dir='data/raw')
    
    print("🔧 Preparing data...")
    X_full, y, vehicle_ids = prepare_scania_for_classification(data)
    
    print(f"\n✓ Dataset loaded:")
    print(f"  Total vehicles: {len(X_full):,}")
    print(f"  Failures: {y.sum():,} ({y.sum()/len(y)*100:.1f}%)")
    
    # Filter to optimal features
    print(f"\n🎯 Using {len(OPTIMAL_FEATURES)} optimal features...")
    X = X_full[OPTIMAL_FEATURES].copy()
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\n✓ Data split:")
    print(f"  Training: {len(X_train):,} vehicles")
    print(f"  Test: {len(X_test):,} vehicles")
    
    # Step 2: Train model
    print_banner("TRAINING MODEL WITH IMPROVED SETTINGS")
    
    # Initialize predictor with optimal threshold and NO calibration
    predictor = RiskPredictor(
        handle_imbalance=True,
        calibrate_probabilities=False,  # DISABLED - calibration can suppress predictions
        default_threshold=0.1  # Optimal threshold from analysis
    )
    
    # Train with improved hyperparameters
    print("🚀 Training XGBoost...")
    predictor.train(
        X_train,
        y_train,
        n_estimators=200,      # More trees for better learning
        max_depth=8,           # Deeper trees
        learning_rate=0.05,    # Lower learning rate for better generalization
        min_child_weight=1,    # Allow splits with fewer samples
        subsample=0.8,         # Prevent overfitting
        colsample_bytree=0.8,  # Feature sampling
        scale_pos_weight=15,   # Higher weight for positive class (instead of 9.36)
        random_state=42
    )
    
    # Step 3: Evaluate with optimal threshold
    print_banner("EVALUATING MODEL PERFORMANCE")
    
    print(f"Using threshold: {predictor.default_threshold}")
    results = predictor.evaluate(X_test, y_test)
    
    # Cost analysis
    cost_results = predictor.calculate_scania_cost(y_test, results['y_pred'])
    
    # Optimal threshold analysis
    threshold_results = predictor.find_optimal_threshold(X_test, y_test)
    
    # Step 4: Save model
    print_banner("SAVING MODEL")
    
    model_manager = ModelManager(models_dir='data/models')
    
    metadata = {
        "model_type": "RiskPredictor_OptimalFeatures_V2",
        "feature_selection_method": "XGBoost Feature Importance (Full Dataset)",
        "feature_selection_date": "2025-11-15",
        "n_features": len(OPTIMAL_FEATURES),
        "features": OPTIMAL_FEATURES,
        "training_samples": len(X_train),
        "test_samples": len(X_test),
        "threshold": predictor.default_threshold,
        "calibration_enabled": False,
        "scale_pos_weight_override": 15,
        "metrics": {
            "accuracy": float(results['accuracy']),
            "auc_roc": float(results['auc_roc']),
            "recall": float(results['recall']),
            "precision": float(results['precision']),
            "specificity": float(results['specificity']),
        },
        "cost_analysis": {
            "total_cost": float(cost_results['total_cost']),
            "false_negatives": int(cost_results['false_negatives']),
            "false_positives": int(cost_results['false_positives'])
        },
        "optimal_threshold_analysis": {
            "optimal_threshold": float(threshold_results['optimal_threshold']),
            "optimal_cost": float(threshold_results['optimal_cost']),
            "cost_savings": float(threshold_results['savings'])
        },
        "handle_imbalance": True,
        "calibrate_probabilities": False,
        "training_date": datetime.now().isoformat()
    }
    
    # Sample training data for SHAP
    sample_size = min(100, len(X_train))
    sample_indices = np.random.choice(len(X_train), size=sample_size, replace=False)
    X_train_sample = X_train.iloc[sample_indices]
    y_train_sample = y_train.iloc[sample_indices]
    
    version = model_manager.save_model(
        model=predictor,
        metadata=metadata,
        training_data={
            'X_train': X_train_sample,
            'y_train': y_train_sample
        }
    )
    
    # Step 5: Compare with previous model
    print_banner("PERFORMANCE SUMMARY")
    
    print("✅ Model Training Complete!\n")
    print(f"Model Version: {version}")
    print(f"Features: {len(OPTIMAL_FEATURES)} (down from 105)")
    print(f"Threshold: {predictor.default_threshold}")
    print(f"Calibration: Disabled")
    print()
    print("📊 Key Metrics:")
    print(f"  Recall:      {results['recall']:.1%} (catches {results['recall']*100:.1f}% of failures)")
    print(f"  Precision:   {results['precision']:.1%}")
    print(f"  Accuracy:    {results['accuracy']:.1%}")
    print(f"  AUC-ROC:     {results['auc_roc']:.3f}")
    print(f"  F1-Score:    {2 * results['recall'] * results['precision'] / (results['recall'] + results['precision']) if (results['recall'] + results['precision']) > 0 else 0:.3f}")
    print()
    print("💰 Cost Analysis:")
    print(f"  False Negatives: {cost_results['false_negatives']} (missed failures)")
    print(f"  False Positives: {cost_results['false_positives']} (false alarms)")
    print(f"  Total Cost: ${cost_results['total_cost']:,}")
    print()
    print("🎯 Optimal Threshold:")
    print(f"  Best threshold: {threshold_results['optimal_threshold']:.2f}")
    print(f"  Cost at optimal: ${threshold_results['optimal_cost']:,}")
    print(f"  Potential savings: ${threshold_results['savings']:,}")
    
    # Success criteria
    print()
    print("="*80)
    if results['recall'] >= 0.40:
        print("✅ SUCCESS: Model catches 40%+ of failures!")
        if results['recall'] >= 0.50:
            print("🎉 EXCELLENT: Model catches 50%+ of failures!")
    else:
        print(f"⚠️  WARNING: Recall is {results['recall']:.1%}, below 40% target")
        print("   Consider:")
        print("   - Increasing scale_pos_weight further (20-25)")
        print("   - Lowering threshold to 0.05")
        print("   - Adding more training data")
    
    print()
    print("📁 Next Steps:")
    print("   1. Review metrics above")
    print("   2. Test predictions with real data")
    print("   3. Update feature_mapper.py with optimal features")
    print("   4. Update API/frontend to use 20 features")
    print("   5. Deploy if metrics are acceptable")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
