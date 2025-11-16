#!/usr/bin/env python3
"""
Quick test to verify new tank data produces varied risk predictions
"""

import pandas as pd
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.model_manager import ModelManager
from core.feature_mapper import rename_features

def test_predictions():
    print("=" * 80)
    print("Testing Predictions on New Tank Data")
    print("=" * 80)
    
    # Load model
    print("\n📦 Loading model...")
    model_manager = ModelManager()
    model_data = model_manager.load_latest_model()
    model = model_data['model']
    print(f"✓ Loaded model")
    
    # Load tank data
    print("\n📊 Loading tank data...")
    df = pd.read_csv('data/examples/1ABCT_1CD_Ironhorse_tanks.csv')
    print(f"✓ Loaded {len(df)} tanks from 1ABCT Ironhorse")
    
    # Convert tank names to model format (Scania codes)
    print("\n🔄 Converting feature names...")
    df_model = rename_features(df, direction='to_scania', preserve_other_columns=True)
    
    # Make predictions
    print("\n🤖 Running predictions...")
    tank_ids = df['TANK_ID'].values
    X = df_model.drop(columns=['TANK_ID'], errors='ignore')
    
    # Get the model's expected feature names and order
    model_features = model.model.feature_names_in_ if hasattr(model.model, 'feature_names_in_') else model.model.get_booster().feature_names
    print(f"Model expects {len(model_features)} features")
    
    # Reorder columns to match model's expected order
    X = X[model_features]
    
    # Use the model's predict_proba method to get failure probabilities
    predictions = model.predict_proba(X)
    
    # Combine results (use correct column names from the new CSV)
    results = pd.DataFrame({
        'TANK_ID': tank_ids,
        'FAILURE_PROBABILITY': predictions,
        'ENGINE_HOURS': df['ENGINE_HOURS'].values,
        'FAULT_CODES': df['FAULT_CODES'].values,
        'TRANSMISSION_CYCLES': df['TRANSMISSION_CYCLES'].values
    })
    
    # Sort by risk
    results_sorted = results.sort_values('FAILURE_PROBABILITY', ascending=False)
    
    # Categorize
    high_risk = results_sorted[results_sorted['FAILURE_PROBABILITY'] >= 0.15]
    medium_risk = results_sorted[(results_sorted['FAILURE_PROBABILITY'] >= 0.05) & 
                                  (results_sorted['FAILURE_PROBABILITY'] < 0.15)]
    low_risk = results_sorted[results_sorted['FAILURE_PROBABILITY'] < 0.05]
    
    print("\n" + "=" * 80)
    print("PREDICTION RESULTS")
    print("=" * 80)
    
    print(f"\n📊 Distribution:")
    print(f"  🔴 High Risk (≥15%):   {len(high_risk)} tanks ({len(high_risk)/len(results)*100:.1f}%)")
    print(f"  🟡 Medium Risk (5-15%): {len(medium_risk)} tanks ({len(medium_risk)/len(results)*100:.1f}%)")
    print(f"  🟢 Low Risk (<5%):      {len(low_risk)} tanks ({len(low_risk)/len(results)*100:.1f}%)")
    
    print(f"\n🔴 Top 5 Highest Risk Tanks:")
    print(results_sorted.head(5).to_string(index=False))
    
    print(f"\n🟢 Top 5 Lowest Risk Tanks:")
    print(results_sorted.tail(5).to_string(index=False))
    
    print(f"\n📈 Statistics:")
    print(f"  Mean Risk: {results['FAILURE_PROBABILITY'].mean():.2%}")
    print(f"  Median Risk: {results['FAILURE_PROBABILITY'].median():.2%}")
    print(f"  Max Risk: {results['FAILURE_PROBABILITY'].max():.2%}")
    print(f"  Min Risk: {results['FAILURE_PROBABILITY'].min():.2%}")
    
    print("\n" + "=" * 80)
    
    # Check if we have variation
    if results['FAILURE_PROBABILITY'].std() > 0.05:
        print("✅ SUCCESS: Model shows significant variation in risk predictions!")
    else:
        print("⚠️ WARNING: Risk predictions still too uniform")
    
    print("=" * 80)

if __name__ == '__main__':
    test_predictions()
