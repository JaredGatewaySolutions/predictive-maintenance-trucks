#!/usr/bin/env python3
"""
Analyze Failure Patterns in Scania Training Data
=================================================
Extract real failure signatures from training data to improve synthetic data generation.

This script analyzes the actual Scania training data to identify:
1. Feature value distributions for failed vs healthy vehicles
2. Statistical thresholds that separate failures from healthy
3. Feature correlations in failed vehicles
4. Percentile ranges for realistic data generation
"""

import sys
import os
import pandas as pd
import numpy as np
import json

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.scania_loader import load_scania_data, prepare_scania_for_classification
from core.feature_mapper import SCANIA_TO_ABRAMS, ALL_SCANIA_FEATURES


def analyze_failure_patterns(data_dir='data/raw'):
    """
    Analyze failure patterns in Scania training data.
    """
    print("="*80)
    print("ANALYZING FAILURE PATTERNS FROM SCANIA TRAINING DATA")
    print("="*80)
    
    # Load data
    print("\n📊 Loading Scania training data...")
    data = load_scania_data(data_dir=data_dir, use_abrams_naming=False, select_top_features=False)
    
    # Prepare for classification
    X, y, vehicle_ids = prepare_scania_for_classification(data, use_last_readout=True, use_abrams_naming=False)
    
    print(f"\n✓ Data loaded:")
    print(f"  Total vehicles: {len(X)}")
    print(f"  Failed vehicles: {y.sum()} ({y.sum()/len(y)*100:.1f}%)")
    print(f"  Healthy vehicles: {len(y) - y.sum()} ({(len(y) - y.sum())/len(y)*100:.1f}%)")
    
    # Focus on the 20 mapped features
    print(f"\n🔍 Analyzing {len(ALL_SCANIA_FEATURES)} mapped features...")
    
    # Filter to only include our 20 features
    available_features = [f for f in ALL_SCANIA_FEATURES if f in X.columns]
    X_filtered = X[available_features].copy()
    
    print(f"  Found {len(available_features)}/{len(ALL_SCANIA_FEATURES)} features")
    
    # Separate failed and healthy vehicles
    X_failed = X_filtered[y == 1]
    X_healthy = X_filtered[y == 0]
    
    print(f"\n📈 Calculating statistics...")
    
    # Calculate statistics for each feature
    patterns = {}
    
    for scania_code in available_features:
        abrams_name = SCANIA_TO_ABRAMS.get(scania_code, scania_code)
        
        # Get data
        failed_values = X_failed[scania_code].dropna()
        healthy_values = X_healthy[scania_code].dropna()
        
        # Calculate percentiles
        failed_percentiles = {
            'min': float(failed_values.min()),
            'p5': float(failed_values.quantile(0.05)),
            'p25': float(failed_values.quantile(0.25)),
            'p50': float(failed_values.quantile(0.50)),
            'p75': float(failed_values.quantile(0.75)),
            'p95': float(failed_values.quantile(0.95)),
            'max': float(failed_values.max()),
            'mean': float(failed_values.mean()),
            'std': float(failed_values.std())
        }
        
        healthy_percentiles = {
            'min': float(healthy_values.min()),
            'p5': float(healthy_values.quantile(0.05)),
            'p25': float(healthy_values.quantile(0.25)),
            'p50': float(healthy_values.quantile(0.50)),
            'p75': float(healthy_values.quantile(0.75)),
            'p95': float(healthy_values.quantile(0.95)),
            'max': float(healthy_values.max()),
            'mean': float(healthy_values.mean()),
            'std': float(healthy_values.std())
        }
        
        # Calculate difference ratio (how much higher are failed vehicles?)
        mean_ratio = failed_percentiles['mean'] / healthy_percentiles['mean'] if healthy_percentiles['mean'] > 0 else 1.0
        median_ratio = failed_percentiles['p50'] / healthy_percentiles['p50'] if healthy_percentiles['p50'] > 0 else 1.0
        
        patterns[scania_code] = {
            'abrams_name': abrams_name,
            'failed': failed_percentiles,
            'healthy': healthy_percentiles,
            'mean_ratio': float(mean_ratio),
            'median_ratio': float(median_ratio),
            'discrimination_power': abs(float(mean_ratio - 1.0))  # How different are they?
        }
    
    # Print summary
    print("\n" + "="*80)
    print("FAILURE PATTERN ANALYSIS RESULTS")
    print("="*80)
    
    # Sort by discrimination power (most different first)
    sorted_patterns = sorted(patterns.items(), key=lambda x: x[1]['discrimination_power'], reverse=True)
    
    print(f"\n🔥 Top 10 Features with Strongest Failure Signals:")
    print(f"{'Rank':<6} {'Abrams Name':<30} {'Failed Mean':<15} {'Healthy Mean':<15} {'Ratio':<10}")
    print("-"*80)
    
    for i, (scania_code, info) in enumerate(sorted_patterns[:10], 1):
        print(f"{i:<6} {info['abrams_name']:<30} {info['failed']['mean']:>14.1f} {info['healthy']['mean']:>14.1f} {info['mean_ratio']:>9.2f}x")
    
    # Print detailed percentile comparison for top features
    print("\n" + "="*80)
    print("DETAILED PERCENTILE COMPARISON (Top 5 Features)")
    print("="*80)
    
    for i, (scania_code, info) in enumerate(sorted_patterns[:5], 1):
        print(f"\n{i}. {info['abrams_name']} ({scania_code})")
        print(f"   {'Percentile':<12} {'Failed':>15} {'Healthy':>15} {'Ratio':>10}")
        print("   " + "-"*55)
        
        for pct in ['p5', 'p25', 'p50', 'p75', 'p95']:
            failed_val = info['failed'][pct]
            healthy_val = info['healthy'][pct]
            ratio = failed_val / healthy_val if healthy_val > 0 else 1.0
            
            pct_label = {
                'p5': '5th %ile',
                'p25': '25th %ile',
                'p50': 'Median',
                'p75': '75th %ile',
                'p95': '95th %ile'
            }[pct]
            
            print(f"   {pct_label:<12} {failed_val:>15.1f} {healthy_val:>15.1f} {ratio:>9.2f}x")
    
    # Save to JSON for generator script
    output_file = 'data/analysis/failure_patterns.json'
    os.makedirs('data/analysis', exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(patterns, f, indent=2)
    
    print(f"\n\n✓ Analysis complete!")
    print(f"📁 Results saved to: {output_file}")
    
    # Print key insights
    print("\n" + "="*80)
    print("KEY INSIGHTS FOR DATA GENERATION")
    print("="*80)
    
    print("\n💡 What makes a vehicle likely to fail?")
    print("\nHigh-risk vehicles should have:")
    
    for i, (scania_code, info) in enumerate(sorted_patterns[:5], 1):
        if info['mean_ratio'] > 1.1:  # Failed vehicles have higher values
            print(f"  • {info['abrams_name']}: {info['mean_ratio']:.2f}x higher than healthy")
            print(f"    → Use range: {info['failed']['p50']:.0f} - {info['failed']['p95']:.0f}")
        elif info['mean_ratio'] < 0.9:  # Failed vehicles have lower values
            print(f"  • {info['abrams_name']}: {info['mean_ratio']:.2f}x lower than healthy")
            print(f"    → Use range: {info['failed']['p5']:.0f} - {info['failed']['p50']:.0f}")
    
    print("\n🔵 Low-risk vehicles should use:")
    print(f"  • Median values from healthy distribution")
    print(f"  • Range: p25 - p75 percentiles")
    
    print("\n" + "="*80)
    
    return patterns


if __name__ == '__main__':
    patterns = analyze_failure_patterns()
