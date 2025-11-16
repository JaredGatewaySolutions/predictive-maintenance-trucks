#!/usr/bin/env python3
"""
Run Feature Importance Analysis
================================
Executable script to analyze feature importance and compare models.

This will:
1. Load the SCaNIa dataset
2. Train a model on ALL 106 features
3. Extract feature importance rankings
4. Select top 20 most important features
5. Retrain with only those 20 features
6. Compare performance metrics
7. Save all results and visualizations

Author: Predictive Maintenance System
"""

import sys
import argparse
from pathlib import Path
from sklearn.model_selection import train_test_split

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.scania_loader import load_scania_data, prepare_scania_for_classification
from core.feature_importance_analyzer import run_full_analysis


def main():
    """Run the feature importance analysis."""
    
    parser = argparse.ArgumentParser(
        description='Analyze feature importance for predictive maintenance model'
    )
    parser.add_argument(
        '--n-features',
        type=int,
        default=20,
        help='Number of top features to select (default: 20)'
    )
    parser.add_argument(
        '--n-samples',
        type=int,
        default=None,
        help='Number of samples to use (default: all available)'
    )
    parser.add_argument(
        '--test-size',
        type=float,
        default=0.2,
        help='Test set proportion (default: 0.2)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='data/analysis',
        help='Directory to save results (default: data/analysis)'
    )
    parser.add_argument(
        '--no-save',
        action='store_true',
        help='Do not save results to files'
    )
    parser.add_argument(
        '--data-dir',
        type=str,
        default='data',
        help='Directory containing SCaNIa data (default: data)'
    )
    
    args = parser.parse_args()
    
    print("╔" + "="*78 + "╗")
    print("║" + "FEATURE IMPORTANCE ANALYSIS - EXECUTION SCRIPT".center(78) + "║")
    print("╚" + "="*78 + "╝\n")
    
    print("Configuration:")
    print(f"  Data directory: {args.data_dir}")
    print(f"  Top features to select: {args.n_features}")
    print(f"  Test size: {args.test_size * 100:.0f}%")
    print(f"  Output directory: {args.output_dir}")
    print(f"  Save results: {not args.no_save}")
    if args.n_samples:
        print(f"  Sample limit: {args.n_samples:,}")
    else:
        print(f"  Sample limit: None (using all data)")
    
    # Step 1: Load data
    print("\n" + "="*80)
    print("LOADING SCANIA DATASET")
    print("="*80)
    
    try:
        data = load_scania_data(data_dir=args.data_dir)
        print("✓ Data loaded successfully")
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        print("\nMake sure the SCaNIa dataset files are in the data directory:")
        print(f"  - {args.data_dir}/train_operational_readouts.csv")
        print(f"  - {args.data_dir}/train_tte.csv")
        return 1
    
    # Step 2: Prepare data
    print("\n" + "="*80)
    print("PREPARING DATA FOR CLASSIFICATION")
    print("="*80)
    
    try:
        X, y, vehicle_ids = prepare_scania_for_classification(data)
        print(f"\n✓ Data prepared:")
        print(f"  Total vehicles: {len(X):,}")
        print(f"  Total features: {X.shape[1]}")
        print(f"  Failures: {y.sum():,} ({y.sum()/len(y)*100:.1f}%)")
        print(f"  Healthy: {(y == 0).sum():,} ({(y == 0).sum()/len(y)*100:.1f}%)")
    except Exception as e:
        print(f"❌ Error preparing data: {e}")
        return 1
    
    # Step 3: Sample if requested
    if args.n_samples and args.n_samples < len(X):
        print(f"\n📊 Sampling {args.n_samples:,} vehicles for faster analysis...")
        import numpy as np
        np.random.seed(42)
        sample_idx = np.random.choice(len(X), size=args.n_samples, replace=False)
        X = X.iloc[sample_idx]
        y = y.iloc[sample_idx]
        vehicle_ids = vehicle_ids.iloc[sample_idx]
        print(f"✓ Sampled data:")
        print(f"  Vehicles: {len(X):,}")
        print(f"  Failures: {y.sum():,} ({y.sum()/len(y)*100:.1f}%)")
    
    # Step 4: Train/test split
    print("\n" + "="*80)
    print("SPLITTING DATA")
    print("="*80)
    
    try:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=args.test_size,
            random_state=42,
            stratify=y
        )
        print(f"\n✓ Data split:")
        print(f"  Training set: {len(X_train):,} vehicles ({len(X_train)/len(X)*100:.0f}%)")
        print(f"  Test set: {len(X_test):,} vehicles ({len(X_test)/len(X)*100:.0f}%)")
        print(f"  Training failures: {y_train.sum():,} ({y_train.sum()/len(y_train)*100:.1f}%)")
        print(f"  Test failures: {y_test.sum():,} ({y_test.sum()/len(y_test)*100:.1f}%)")
    except Exception as e:
        print(f"❌ Error splitting data: {e}")
        return 1
    
    # Step 5: Run analysis
    print("\n" + "="*80)
    print("RUNNING FEATURE IMPORTANCE ANALYSIS")
    print("="*80)
    print("\nThis will:")
    print("  1. Train on ALL features")
    print("  2. Extract feature importance")
    print(f"  3. Select top {args.n_features} features")
    print("  4. Retrain on reduced feature set")
    print("  5. Compare performance")
    print()
    
    try:
        results = run_full_analysis(
            X_train=X_train,
            y_train=y_train,
            X_test=X_test,
            y_test=y_test,
            n_top_features=args.n_features,
            save_results=not args.no_save,
            output_dir=args.output_dir
        )
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Step 6: Display summary
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + "ANALYSIS SUMMARY".center(78) + "║")
    print("╚" + "="*78 + "╝\n")
    
    print(f"Top {args.n_features} Most Important Features:")
    print("-" * 80)
    importance_df = results['importance_df'].head(args.n_features)
    for i, (_, row) in enumerate(importance_df.iterrows(), 1):
        print(f"  {i:2d}. {row['feature']:<15} - {row['importance']:>8.1f} ({row['importance_pct']:>5.2f}%)")
    
    cumulative = importance_df['cumulative_pct'].iloc[-1]
    print(f"\n  → These {args.n_features} features capture {cumulative:.1f}% of total importance")
    
    print("\n" + "Performance Comparison:")
    print("-" * 80)
    
    full_res = results['full_results']
    reduced_res = results['reduced_results']
    
    comparison_metrics = [
        ('Accuracy', 'accuracy', '.4f'),
        ('AUC-ROC', 'auc_roc', '.4f'),
        ('Recall', 'recall', '.4f'),
        ('Precision', 'precision', '.4f'),
        ('F1-Score', 'f1_score', '.4f'),
        ('Total Cost', 'total_cost', ',.0f')
    ]
    
    print(f"{'Metric':<20} {'Full Model':<20} {'Reduced Model':<20} {'Change':<15}")
    print("-" * 80)
    
    for metric_name, metric_key, fmt in comparison_metrics:
        full_val = full_res.get(metric_key, 0)
        reduced_val = reduced_res.get(metric_key, 0)
        
        if metric_key == 'total_cost':
            full_str = f"${full_val:{fmt}}"
            reduced_str = f"${reduced_val:{fmt}}"
            diff = reduced_val - full_val
            if full_val > 0:
                pct_change = (diff / full_val) * 100
                change_str = f"${diff:+,.0f} ({pct_change:+.1f}%)"
            else:
                change_str = f"${diff:+,.0f}"
        else:
            full_str = f"{full_val:{fmt}}"
            reduced_str = f"{reduced_val:{fmt}}"
            diff = reduced_val - full_val
            if full_val > 0:
                pct_change = (diff / full_val) * 100
                change_str = f"{diff:+{fmt}} ({pct_change:+.1f}%)"
            else:
                change_str = f"{diff:+{fmt}}"
        
        print(f"{metric_name:<20} {full_str:<20} {reduced_str:<20} {change_str:<15}")
    
    # Recommendation
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + "RECOMMENDATION".center(78) + "║")
    print("╚" + "="*78 + "╝\n")
    
    full_recall = full_res.get('recall', 0)
    reduced_recall = reduced_res.get('recall', 0)
    full_cost = full_res.get('total_cost', 0)
    reduced_cost = reduced_res.get('total_cost', 0)
    
    if reduced_recall >= full_recall * 0.95 and reduced_cost <= full_cost * 1.1:
        print("✅ RECOMMENDATION: Use the reduced feature set!")
        print(f"   • Reduces features from {X_train.shape[1]} to {args.n_features} ({args.n_features/X_train.shape[1]*100:.1f}%)")
        print(f"   • Maintains similar performance (recall: {reduced_recall:.3f} vs {full_recall:.3f})")
        print(f"   • Much easier for users to provide {args.n_features} inputs vs {X_train.shape[1]}")
        print(f"   • Faster inference and simpler explainability")
    elif reduced_recall < full_recall * 0.8:
        print("⚠️ WARNING: Reduced model has significantly lower recall")
        print(f"   • Reduced recall: {reduced_recall:.3f} vs Full: {full_recall:.3f}")
        print(f"   • May miss too many failures")
        print(f"   • Consider using top {args.n_features * 2} features instead")
    else:
        print("ℹ️ MIXED RESULTS:")
        print(f"   • Reduced model recall: {reduced_recall:.3f} vs Full: {full_recall:.3f}")
        print(f"   • Cost difference: ${reduced_cost - full_cost:+,.0f}")
        print(f"   • Review the detailed metrics above to decide")
    
    if not args.no_save:
        print(f"\n📁 Results saved to: {args.output_dir}")
        print("   • Feature importance rankings (CSV)")
        print("   • Top features list (JSON)")
        print("   • Model comparison metrics (JSON)")
        print("   • Feature importance plot (PNG)")
    
    print("\n✓ Analysis complete!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
