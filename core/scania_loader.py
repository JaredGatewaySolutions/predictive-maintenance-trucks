#!/usr/bin/env python3
"""
SCANIA Dataset Loader
=====================
Helper script to load and prepare SCANIA Component X dataset for analysis.

Dataset available at: https://doi.org/10.5878/jvb5-d390

NOTE: This script expects CSV files to be in the 'data/' subdirectory
"""

import pandas as pd
import numpy as np
import os

def load_scania_data(data_dir='data/raw'):
    """
    Load SCANIA Component X dataset files.
    
    Args:
        data_dir: Directory containing SCANIA CSV files (default: 'data/')
        
    Returns:
        Dictionary with training, validation, and test data
    """
    
    print("="*80)
    print("LOADING SCANIA COMPONENT X DATASET")
    print("="*80)
    print(f"Data directory: {data_dir}")
    
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
            print(f"   Loading {filename}...")
            data[f'train_{key}'] = pd.read_csv(filepath)
            print(f"   ✓ {filename}: {data[f'train_{key}'].shape}")
        else:
            print(f"   ✗ {filename}: NOT FOUND at {filepath}")
    
    # Load validation data
    print("\n2. Loading Validation Data...")
    for key, filename in val_files.items():
        filepath = os.path.join(data_dir, filename)
        if os.path.exists(filepath):
            print(f"   Loading {filename}...")
            data[f'val_{key}'] = pd.read_csv(filepath)
            print(f"   ✓ {filename}: {data[f'val_{key}'].shape}")
        else:
            print(f"   ✗ {filename}: NOT FOUND at {filepath}")
    
    # Load test data
    print("\n3. Loading Test Data...")
    for key, filename in test_files.items():
        filepath = os.path.join(data_dir, filename)
        if os.path.exists(filepath):
            print(f"   Loading {filename}...")
            data[f'test_{key}'] = pd.read_csv(filepath)
            print(f"   ✓ {filename}: {data[f'test_{key}'].shape}")
        else:
            print(f"   ✗ {filename}: NOT FOUND at {filepath}")
    
    return data


def prepare_scania_for_classification(data, use_last_readout=True):
    """
    Prepare SCANIA data for classification (failure prediction).
    
    Args:
        data: Dictionary from load_scania_data()
        use_last_readout: If True, use last readout per vehicle (default: True)
        
    Returns:
        X, y, vehicle_ids for training
    """
    print("\n" + "="*80)
    print("PREPARING DATA FOR CLASSIFICATION")
    print("="*80)
    
    # Get operational data
    train_operational = data.get('train_operational')
    train_tte = data.get('train_tte')
    
    if train_operational is None or train_tte is None:
        print("✗ Missing required training files")
        return None, None, None
    
    print(f"Raw operational data: {train_operational.shape}")
    print(f"Time-to-event data: {train_tte.shape}")
    
    # Get last readout for each vehicle
    if use_last_readout:
        print("\nExtracting last readout for each vehicle...")
        last_readouts = train_operational.groupby('vehicle_id').last().reset_index()
        print(f"Last readouts: {last_readouts.shape}")
    else:
        last_readouts = train_operational
    
    # Merge with time-to-event data
    # Note: train_tte is indexed by vehicle_id position, not vehicle_id itself
    # We need to merge carefully
    print("\nMerging operational data with failure labels...")
    
    # Get unique vehicle IDs in order
    unique_vehicles = train_operational['vehicle_id'].unique()
    print(f"Unique vehicles: {len(unique_vehicles)}")
    
    # Create a mapping of vehicle_id to TTE data
    train_tte_indexed = train_tte.copy()
    train_tte_indexed['vehicle_id'] = unique_vehicles
    
    # Merge
    merged = last_readouts.merge(train_tte_indexed, on='vehicle_id', how='inner')
    print(f"Merged data: {merged.shape}")
    
    # Prepare features (drop non-feature columns)
    feature_cols = [col for col in merged.columns 
                   if col not in ['vehicle_id', 'time_step', 'in_study_repair', 'length_of_study_time_step']]
    
    X = merged[feature_cols].fillna(0)
    y = merged['in_study_repair']
    vehicle_ids = merged['vehicle_id']
    
    print(f"\n✓ Features prepared:")
    print(f"  - Samples: {len(X)}")
    print(f"  - Features: {len(feature_cols)}")
    print(f"  - Target variable: in_study_repair")
    print(f"  - Positive class (failures): {y.sum()} ({y.sum()/len(y)*100:.1f}%)")
    print(f"  - Negative class (healthy): {len(y)-y.sum()} ({(len(y)-y.sum())/len(y)*100:.1f}%)")
    print(f"  - Imbalance ratio: {(len(y)-y.sum())/y.sum():.1f}:1")
    
    return X, y, vehicle_ids


def prepare_scania_for_survival(data):
    """
    Prepare SCANIA data for survival analysis.
    
    Args:
        data: Dictionary from load_scania_data()
        
    Returns:
        DataFrame with duration, event, and feature columns
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
    
    # Get unique vehicle IDs
    unique_vehicles = train_operational['vehicle_id'].unique()
    
    # Create indexed TTE data
    train_tte_indexed = train_tte.copy()
    train_tte_indexed['vehicle_id'] = unique_vehicles
    
    # Merge with TTE data
    survival_data = last_readouts.merge(train_tte_indexed, on='vehicle_id', how='inner')
    
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
      - Variable 167: 10 bins (e.g., distance driven in different temp ranges)
      - Variable 272: 10 bins
      - Variable 291: 11 bins
      - Variable 158: 10 bins
      - Variable 459: 20 bins
      - Variable 397: 36 bins
    
    • Numerical counters: 8 variables
      - 171_0, 666_0, 427_0, 837_0, 309_0, 835_0, 370_0, 100_0
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
    2. Regression: Predict time-to-failure (RUL)
    3. Survival Analysis: Calculate survival probabilities
    4. Explainability: WHY will this vehicle fail?
    
    FILES STRUCTURE:
    ===============
    
    data/
      ├── train_operational_readouts.csv   (1.2M readouts, 23.5K vehicles)
      ├── train_tte.csv                    (Time-to-event labels)
      ├── train_specifications.csv         (Vehicle specs)
      ├── validation_operational_readouts.csv
      ├── validation_labels.csv
      ├── validation_specifications.csv
      ├── test_operational_readouts.csv
      ├── test_labels.csv
      └── test_specifications.csv
    
    DOWNLOAD:
    ========
    1. Go to: https://doi.org/10.5878/jvb5-d390
    2. Download all CSV files
    3. Place in 'data/' subdirectory
    4. Run: python scania_loader.py
    
    ══════════════════════════════════════════════════════════════════════════════
    """)


if __name__ == "__main__":
    # Display info
    get_scania_info()
    
    # Try to load data
    print("\n" + "="*80)
    print("ATTEMPTING TO LOAD DATA FROM data/ DIRECTORY")
    print("="*80)
    
    data = load_scania_data(data_dir='data')
    
    if 'train_operational' in data:
        print("\n✓ Data loaded successfully!")
        print("\nYou can now use this data for analysis:")
        print("\nExample:")
        print("  from scania_loader import load_scania_data, prepare_scania_for_classification")
        print("  from explainability_analyzer import ExplainabilityAnalyzer")
        print("  from sklearn.ensemble import RandomForestClassifier")
        print()
        print("  # Load data")
        print("  data = load_scania_data()")
        print("  X, y, vehicle_ids = prepare_scania_for_classification(data)")
        print()
        print("  # Train model")
        print("  model = RandomForestClassifier(n_estimators=100, random_state=42)")
        print("  model.fit(X, y)")
        print()
        print("  # Explain predictions")
        print("  analyzer = ExplainabilityAnalyzer(model, X, y)")
        print("  analyzer.initialize_shap()")
        print("  analyzer.explain_prediction(X.iloc[0], instance_id=vehicle_ids.iloc[0])")
    else:
        print("\n" + "="*80)
        print("DATA NOT FOUND")
        print("="*80)
        print("\nPlease ensure SCANIA dataset files are in the 'data/' directory.")
        print("Download from: https://doi.org/10.5878/jvb5-d390")
