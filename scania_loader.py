#!/usr/bin/env python3
"""
SCANIA Dataset Loader
=====================
Helper script to load and prepare SCANIA Component X dataset for analysis.

Dataset available at: https://doi.org/10.5878/jvb5-d390
"""

import pandas as pd
import numpy as np
import os

def load_scania_data(data_dir='.'):
    """
    Load SCANIA Component X dataset files.
    
    Args:
        data_dir: Directory containing SCANIA CSV files
        
    Returns:
        Dictionary with training, validation, and test data
    """
    
    print("="*80)
    print("LOADING SCANIA COMPONENT X DATASET")
    print("="*80)
    
    data = {}
    
    # Training set files
    train_files = {
        'operational': 'train_operational_readouts.csv',
        'tte': 'train_tte.csv',
        'specifications': 'train_specifications.csv'
    }
    
    # Validation set files
    val_files = {
        'operational': 'validation_operational_readouts.csv',
        'labels': 'validation_labels.csv',
        'specifications': 'validation_specifications.csv'
    }
    
    # Test set files
    test_files = {
        'operational': 'test_operational_readouts.csv',
        'labels': 'test_labels.csv',
        'specifications': 'test_specifications.csv'
    }
    
    # Load training data
    print("\n1. Loading Training Data...")
    for key, filename in train_files.items():
        filepath = os.path.join(data_dir, filename)
        if os.path.exists(filepath):
            data[f'train_{key}'] = pd.read_csv(filepath)
            print(f"   ✓ {filename}: {data[f'train_{key}'].shape}")
        else:
            print(f"   ✗ {filename}: NOT FOUND")
    
    # Load validation data
    print("\n2. Loading Validation Data...")
    for key, filename in val_files.items():
        filepath = os.path.join(data_dir, filename)
        if os.path.exists(filepath):
            data[f'val_{key}'] = pd.read_csv(filepath)
            print(f"   ✓ {filename}: {data[f'val_{key}'].shape}")
        else:
            print(f"   ✗ {filename}: NOT FOUND")
    
    # Load test data
    print("\n3. Loading Test Data...")
    for key, filename in test_files.items():
        filepath = os.path.join(data_dir, filename)
        if os.path.exists(filepath):
            data[f'test_{key}'] = pd.read_csv(filepath)
            print(f"   ✓ {filename}: {data[f'test_{key}'].shape}")
        else:
            print(f"   ✗ {filename}: NOT FOUND")
    
    return data


def prepare_scania_for_classification(data):
    """
    Prepare SCANIA data for classification (failure prediction).
    
    Args:
        data: Dictionary from load_scania_data()
        
    Returns:
        X, y for training
    """
    print("\n" + "="*80)
    print("PREPARING DATA FOR CLASSIFICATION")
    print("="*80)
    
    # Get operational data
    train_operational = data.get('train_operational')
    train_tte = data.get('train_tte')
    
    if train_operational is None or train_tte is None:
        print("✗ Missing required training files")
        return None, None
    
    # Merge operational data with labels
    # Group by vehicle_id and get last readout for each vehicle
    last_readouts = train_operational.groupby('vehicle_id').last().reset_index()
    
    # Merge with time-to-event data
    merged = last_readouts.merge(train_tte, left_index=True, right_index=True)
    
    # Prepare features (drop non-feature columns)
    feature_cols = [col for col in merged.columns 
                   if col not in ['vehicle_id', 'time_step', 'in_study_repair', 'length_of_study_time_step']]
    
    X = merged[feature_cols].fillna(0)
    y = merged['in_study_repair']
    
    print(f"\n✓ Features prepared:")
    print(f"  - Samples: {len(X)}")
    print(f"  - Features: {len(feature_cols)}")
    print(f"  - Target variable: in_study_repair")
    print(f"  - Positive class: {y.sum()} ({y.sum()/len(y)*100:.1f}%)")
    print(f"  - Negative class: {len(y)-y.sum()} ({(len(y)-y.sum())/len(y)*100:.1f}%)")
    
    return X, y


def prepare_scania_for_survival(data):
    """
    Prepare SCANIA data for survival analysis.
    
    Args:
        data: Dictionary from load_scania_data()
        
    Returns:
        DataFrame with duration and event columns
    """
    print("\n" + "="*80)
    print("PREPARING DATA FOR SURVIVAL ANALYSIS")
    print("="*80)
    
    train_operational = data.get('train_operational')
    train_tte = data.get('train_tte')
    
    if train_operational is None or train_tte is None:
        print("✗ Missing required training files")
        return None
    
    # Get features from last readout
    last_readouts = train_operational.groupby('vehicle_id').last().reset_index()
    
    # Merge with TTE data
    survival_data = last_readouts.merge(train_tte, left_index=True, right_index=True)
    
    # Prepare for survival analysis
    survival_data['duration'] = survival_data['length_of_study_time_step']
    survival_data['event'] = survival_data['in_study_repair']
    
    print(f"\n✓ Survival data prepared:")
    print(f"  - Samples: {len(survival_data)}")
    print(f"  - Events (failures): {survival_data['event'].sum()}")
    print(f"  - Censored: {len(survival_data) - survival_data['event'].sum()}")
    print(f"  - Mean duration: {survival_data['duration'].mean():.1f} time steps")
    print(f"  - Median duration: {survival_data['duration'].median():.1f} time steps")
    
    return survival_data


def get_scania_info():
    """Display information about the SCANIA dataset."""
    
    print("""
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║                      SCANIA COMPONENT X DATASET                              ║
    ║                  Real-World Heavy-Duty Truck Dataset                         ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    
    DATASET OVERVIEW:
    ================
    
    Source: SCANIA CV AB & Stockholm University
    Publication: Nature Scientific Data (2025)
    DOI: https://doi.org/10.5878/jvb5-d390
    
    SIZE:
    • Total vehicles: 33,000+
    • Training set: 23,550 vehicles, 1,122,452 readouts
    • Validation set: 5,046 vehicles, 196,227 readouts
    • Test set: 5,045 vehicles, 198,140 readouts
    
    FEATURES:
    • 107 total features (14 original variables)
    • Histogram features: 6 variables (97 bins total)
      - Variable 167: 10 bins
      - Variable 272: 10 bins
      - Variable 291: 11 bins
      - Variable 158: 10 bins
      - Variable 459: 20 bins
      - Variable 397: 36 bins
    
    • Numerical counters: 8 variables
      - All are accumulative, suitable for trend analysis
    
    • Specifications: 8 categorical features
      - Engine type, wheel configuration, etc.
      - Anonymized as Cat0, Cat1, ..., Cat28
    
    TARGET:
    • Binary classification: Component failure (Yes/No)
    • Imbalanced: ~90% healthy, ~10% failed
    • Time-to-event data available for survival analysis
    
    USE CASES:
    1. Classification: Predict imminent failures
    2. Regression: Predict time-to-failure
    3. Survival Analysis: Calculate survival probabilities
    4. Anomaly Detection: Identify unusual patterns
    
    FILES NEEDED:
    ============
    
    Training Set:
    • train_operational_readouts.csv  - Time series sensor data
    • train_tte.csv                   - Time-to-event (failure) data
    • train_specifications.csv        - Vehicle specifications
    
    Validation Set:
    • validation_operational_readouts.csv
    • validation_labels.csv
    • validation_specifications.csv
    
    Test Set:
    • test_operational_readouts.csv
    • test_labels.csv
    • test_specifications.csv
    
    DOWNLOAD:
    ========
    1. Go to: https://doi.org/10.5878/jvb5-d390
    2. Download all CSV files
    3. Place in same directory as this script
    4. Run: python scania_loader.py
    
    ══════════════════════════════════════════════════════════════════════════════
    """)


if __name__ == "__main__":
    # Display info
    get_scania_info()
    
    # Try to load data
    print("\n" + "="*80)
    print("ATTEMPTING TO LOAD DATA FROM CURRENT DIRECTORY")
    print("="*80)
    
    data = load_scania_data()
    
    if 'train_operational' in data:
        print("\n✓ Data loaded successfully!")
        print("\nYou can now use this data with the predictive maintenance analyzer:")
        print("\nExample:")
        print("  from predictive_maintenance_demo import PredictiveMaintenanceAnalyzer")
        print("  X, y = prepare_scania_for_classification(data)")
        print("  analyzer = PredictiveMaintenanceAnalyzer(data_df=pd.concat([X, y], axis=1))")
        print("  analyzer.run_full_analysis(target_col='in_study_repair')")
    else:
        print("\n" + "="*80)
        print("DATA NOT FOUND")
        print("="*80)
        print("\nPlease download SCANIA dataset files and place them in this directory.")
        print("Download from: https://doi.org/10.5878/jvb5-d390")
