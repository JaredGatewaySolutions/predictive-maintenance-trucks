#!/usr/bin/env python3
"""
Feature Mapper - M1 Abrams Tank Sensor Mapping
===============================================
Maps anonymized Scania dataset features to realistic M1 Abrams tank sensor names.

This module provides bidirectional mapping between:
- Original Scania dataset codes (171_0, 666_0, etc.)
- Military-grade M1 Abrams sensor names (ENGINE_HOURS, FAULT_CODES, etc.)

Author: Predictive Maintenance System
Context: M1 Abrams Tank Fleet Management
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union
import logging

# Configure logging
logger = logging.getLogger(__name__)

# ============================================================================
# FEATURE MAPPING: SCANIA → M1 ABRAMS
# ============================================================================

# Forward mapping: Scania technical codes → M1 Abrams military sensor names
SCANIA_TO_ABRAMS = {
    # Primary Numerical Counters (8 features)
    '171_0': 'ENGINE_HOURS',           # Total turbine engine operating hours
    '666_0': 'FAULT_CODES',            # Diagnostic trouble codes count
    '427_0': 'COMBAT_STRESS_EVENTS',   # High-stress operational events
    '837_0': 'IDLE_HOURS',             # Engine idle time
    '309_0': 'TRACK_MILES',            # Total track system mileage
    '835_0': 'TURRET_ROTATIONS',       # Cumulative turret rotation cycles
    '370_0': 'MAIN_GUN_ROUNDS',        # Main gun rounds fired
    '100_0': 'TRANSMISSION_SHIFTS',    # Total transmission shift count
    
    # Temperature Operations (4 bins from feature 167)
    '167_0': 'TEMP_EXTREME_COLD_MI',   # Miles in extreme cold (<-20°C)
    '167_3': 'TEMP_COLD_MI',           # Miles in cold (-20 to 0°C)
    '167_6': 'TEMP_MODERATE_MI',       # Miles in moderate temp (0-30°C)
    '167_9': 'TEMP_HOT_MI',            # Miles in hot/desert (>30°C)
    
    # Load Conditions (4 bins from feature 272)
    '272_0': 'LOAD_MINIMAL_MI',        # Miles with minimal load
    '272_3': 'LOAD_STANDARD_MI',       # Miles at standard combat weight
    '272_6': 'LOAD_HEAVY_MI',          # Miles with heavy load
    '272_9': 'LOAD_MAXIMUM_MI',        # Miles at maximum weight capacity
    
    # Terrain Types (4 bins from feature 291)
    '291_0': 'TERRAIN_PAVED_MI',       # Miles on roads/paved surfaces
    '291_3': 'TERRAIN_DIRT_MI',        # Miles on dirt/unpaved
    '291_6': 'TERRAIN_ROUGH_MI',       # Miles on rough terrain
    '291_9': 'TERRAIN_EXTREME_MI',     # Miles on extreme terrain (mud, sand)
}

# Reverse mapping: M1 Abrams military sensor names → Scania technical codes
ABRAMS_TO_SCANIA = {v: k for k, v in SCANIA_TO_ABRAMS.items()}

# ============================================================================
# FEATURE DESCRIPTIONS
# ============================================================================

FEATURE_DESCRIPTIONS = {
    'ENGINE_HOURS': 'Total turbine engine operating hours',
    'FAULT_CODES': 'Cumulative diagnostic trouble codes detected',
    'COMBAT_STRESS_EVENTS': 'High-stress operational events (combat, training)',
    'IDLE_HOURS': 'Engine idle time during maintenance or staging',
    'TRACK_MILES': 'Total track system mileage',
    'TURRET_ROTATIONS': 'Cumulative turret rotation cycles',
    'MAIN_GUN_ROUNDS': 'Main gun rounds fired (barrel wear indicator)',
    'TRANSMISSION_SHIFTS': 'Total transmission shift count',
    'TEMP_EXTREME_COLD_MI': 'Miles operated in extreme cold conditions (<-20°C)',
    'TEMP_COLD_MI': 'Miles operated in cold conditions (-20 to 0°C)',
    'TEMP_MODERATE_MI': 'Miles in moderate temperature (0-30°C)',
    'TEMP_HOT_MI': 'Miles in hot/desert conditions (>30°C)',
    'LOAD_MINIMAL_MI': 'Miles with minimal payload',
    'LOAD_STANDARD_MI': 'Miles at standard combat weight',
    'LOAD_HEAVY_MI': 'Miles with heavy load configuration',
    'LOAD_MAXIMUM_MI': 'Miles at maximum weight capacity',
    'TERRAIN_PAVED_MI': 'Miles on roads/paved surfaces',
    'TERRAIN_DIRT_MI': 'Miles on dirt/unpaved roads',
    'TERRAIN_ROUGH_MI': 'Miles on rough terrain',
    'TERRAIN_EXTREME_MI': 'Miles on extreme terrain (mud, sand, obstacles)'
}

# Feature categories for grouping
FEATURE_CATEGORIES = {
    'Operational Counters': [
        'ENGINE_HOURS', 'IDLE_HOURS', 'TRACK_MILES', 
        'TURRET_ROTATIONS', 'MAIN_GUN_ROUNDS', 'TRANSMISSION_SHIFTS'
    ],
    'Diagnostics': [
        'FAULT_CODES', 'COMBAT_STRESS_EVENTS'
    ],
    'Environmental Operations': [
        'TEMP_EXTREME_COLD_MI', 'TEMP_COLD_MI', 
        'TEMP_MODERATE_MI', 'TEMP_HOT_MI'
    ],
    'Load Conditions': [
        'LOAD_MINIMAL_MI', 'LOAD_STANDARD_MI',
        'LOAD_HEAVY_MI', 'LOAD_MAXIMUM_MI'
    ],
    'Terrain Operations': [
        'TERRAIN_PAVED_MI', 'TERRAIN_DIRT_MI',
        'TERRAIN_ROUGH_MI', 'TERRAIN_EXTREME_MI'
    ]
}

# List of all 20 selected features in display order
ALL_ABRAMS_FEATURES = list(SCANIA_TO_ABRAMS.values())
ALL_SCANIA_FEATURES = list(SCANIA_TO_ABRAMS.keys())

# ============================================================================
# MAPPING FUNCTIONS
# ============================================================================

def rename_features(
    df: pd.DataFrame,
    direction: str = 'to_abrams',
    preserve_other_columns: bool = True
) -> pd.DataFrame:
    """
    Rename DataFrame columns between Scania codes and M1 Abrams names.
    
    Args:
        df: DataFrame with feature columns
        direction: 'to_abrams' or 'to_scania'
        preserve_other_columns: Keep columns not in mapping (like vehicle_id, time_step)
    
    Returns:
        DataFrame with renamed columns
    
    Examples:
        >>> df_abrams = rename_features(df_scania, direction='to_abrams')
        >>> df_scania = rename_features(df_abrams, direction='to_scania')
    """
    if direction == 'to_abrams':
        mapping = SCANIA_TO_ABRAMS
    elif direction == 'to_scania':
        mapping = ABRAMS_TO_SCANIA
    else:
        raise ValueError(f"Invalid direction: {direction}. Use 'to_abrams' or 'to_scania'")
    
    # Create new column mapping
    new_columns = {}
    for col in df.columns:
        if col in mapping:
            new_columns[col] = mapping[col]
        elif preserve_other_columns:
            new_columns[col] = col  # Keep as-is
    
    # Rename
    df_renamed = df.rename(columns=new_columns)
    
    return df_renamed


def select_features(
    df: pd.DataFrame,
    feature_type: str = 'scania'
) -> pd.DataFrame:
    """
    Select only the 20 mapped features from a larger dataset.
    
    Args:
        df: DataFrame with many features
        feature_type: 'scania' (codes like 171_0) or 'abrams' (names like ENGINE_HOURS)
    
    Returns:
        DataFrame with only the 20 selected features (plus vehicle_id, time_step if present)
    """
    # Determine which features to select
    if feature_type == 'scania':
        features_to_select = ALL_SCANIA_FEATURES
    elif feature_type == 'abrams':
        features_to_select = ALL_ABRAMS_FEATURES
    else:
        raise ValueError(f"Invalid feature_type: {feature_type}")
    
    # Always preserve these columns if they exist
    preserve_cols = ['vehicle_id', 'time_step', 'tank_id']
    
    # Build final column list
    columns_to_keep = []
    for col in df.columns:
        if col in preserve_cols or col in features_to_select:
            columns_to_keep.append(col)
    
    # Select columns
    df_selected = df[columns_to_keep].copy()
    
    logger.info(f"Selected {len(features_to_select)} features from {df.shape[1]} total columns")
    
    return df_selected


def validate_abrams_data(
    df: pd.DataFrame,
    require_all: bool = True,
    allow_extra: bool = True
) -> Dict[str, Union[bool, List[str]]]:
    """
    Validate that DataFrame has M1 Abrams feature columns.
    
    Args:
        df: DataFrame to validate
        require_all: All 20 features must be present
        allow_extra: Allow extra columns beyond the 20 features
    
    Returns:
        Dictionary with validation results:
        {
            'valid': bool,
            'missing_features': List[str],
            'extra_features': List[str],
            'message': str
        }
    """
    df_features = set(df.columns)
    required_features = set(ALL_ABRAMS_FEATURES)
    
    missing = required_features - df_features
    extra = df_features - required_features - {'vehicle_id', 'time_step', 'tank_id'}
    
    valid = True
    messages = []
    
    if require_all and missing:
        valid = False
        messages.append(f"Missing {len(missing)} required features: {list(missing)[:5]}...")
    
    if not allow_extra and extra:
        valid = False
        messages.append(f"Unexpected {len(extra)} columns: {list(extra)[:5]}...")
    
    if valid:
        messages.append(f"✓ Valid M1 Abrams data format with {len(df_features & required_features)} features")
    
    return {
        'valid': valid,
        'missing_features': list(missing),
        'extra_features': list(extra),
        'message': ' | '.join(messages)
    }


def validate_scania_data(
    df: pd.DataFrame,
    require_all: bool = True,
    allow_extra: bool = True
) -> Dict[str, Union[bool, List[str]]]:
    """
    Validate that DataFrame has Scania feature codes.
    
    Args:
        df: DataFrame to validate
        require_all: All 20 features must be present
        allow_extra: Allow extra columns beyond the 20 features
    
    Returns:
        Dictionary with validation results
    """
    df_features = set(df.columns)
    required_features = set(ALL_SCANIA_FEATURES)
    
    missing = required_features - df_features
    extra = df_features - required_features - {'vehicle_id', 'time_step', 'tank_id'}
    
    valid = True
    messages = []
    
    if require_all and missing:
        valid = False
        messages.append(f"Missing {len(missing)} required features: {list(missing)[:5]}...")
    
    if not allow_extra and extra:
        valid = False
        messages.append(f"Unexpected {len(extra)} columns: {list(extra)[:5]}...")
    
    if valid:
        messages.append(f"✓ Valid Scania data format with {len(df_features & required_features)} features")
    
    return {
        'valid': valid,
        'missing_features': list(missing),
        'extra_features': list(extra),
        'message': ' | '.join(messages)
    }


def auto_detect_format(df: pd.DataFrame) -> str:
    """
    Auto-detect if DataFrame uses Scania codes or Abrams names.
    
    Args:
        df: DataFrame to analyze
    
    Returns:
        'scania', 'abrams', or 'unknown'
    """
    df_features = set(df.columns)
    
    scania_matches = len(df_features & set(ALL_SCANIA_FEATURES))
    abrams_matches = len(df_features & set(ALL_ABRAMS_FEATURES))
    
    if scania_matches > abrams_matches and scania_matches >= 5:
        return 'scania'
    elif abrams_matches > scania_matches and abrams_matches >= 5:
        return 'abrams'
    else:
        return 'unknown'


def convert_to_model_format(
    df: pd.DataFrame,
    auto_detect: bool = True,
    pad_missing_features: bool = True,
    expected_features: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Convert any format to model-ready format (Scania codes).
    
    The model was trained on Scania codes, so predictions need Scania format.
    This function auto-detects the input format and converts if needed.
    
    Args:
        df: DataFrame in any format
        auto_detect: Automatically detect format
        pad_missing_features: Pad missing features with zeros
        expected_features: List of expected feature names (from model metadata)
    
    Returns:
        DataFrame in Scania code format (model-ready)
    """
    # Preserve ID columns
    preserve_cols = ['vehicle_id', 'time_step', 'tank_id']
    id_data = df[[col for col in preserve_cols if col in df.columns]].copy()
    
    if auto_detect:
        format_type = auto_detect_format(df)
        
        if format_type == 'abrams':
            logger.info("📊 Detected M1 Abrams format, converting to model format...")
            df = rename_features(df, direction='to_scania')
        elif format_type == 'scania':
            logger.info("✓ Already in model format (Scania codes)")
        else:
            logger.warning("⚠️ Warning: Could not auto-detect format, assuming Scania codes")
    
    # Select only the 20 mapped features (if they exist)
    available_features = [col for col in df.columns if col in ALL_SCANIA_FEATURES]
    df_selected = df[available_features].copy()
    
    logger.info(f"Found {len(available_features)} of {len(ALL_SCANIA_FEATURES)} mapped features")
    
    # If we have expected features from the model and need to pad
    if pad_missing_features and expected_features:
        logger.info(f"Padding to match model's {len(expected_features)} expected features...")
        
        # Add missing features with zeros
        for feature in expected_features:
            if feature not in df_selected.columns:
                df_selected[feature] = 0.0
        
        # Reorder columns to match expected order
        df_selected = df_selected[expected_features]
        
        logger.info(f"✓ Padded DataFrame now has {df_selected.shape[1]} features")
    
    # Restore ID columns
    for col in id_data.columns:
        df_selected[col] = id_data[col].values
    
    return df_selected


def get_feature_info(feature_name: str) -> Dict[str, str]:
    """
    Get information about a specific feature.
    
    Args:
        feature_name: Either Scania code or Abrams name
    
    Returns:
        Dictionary with feature information
    """
    # Check if it's a Scania code
    if feature_name in SCANIA_TO_ABRAMS:
        abrams_name = SCANIA_TO_ABRAMS[feature_name]
        return {
            'scania_code': feature_name,
            'abrams_name': abrams_name,
            'description': FEATURE_DESCRIPTIONS.get(abrams_name, 'No description'),
            'format': 'scania'
        }
    
    # Check if it's an Abrams name
    elif feature_name in ABRAMS_TO_SCANIA:
        scania_code = ABRAMS_TO_SCANIA[feature_name]
        return {
            'scania_code': scania_code,
            'abrams_name': feature_name,
            'description': FEATURE_DESCRIPTIONS.get(feature_name, 'No description'),
            'format': 'abrams'
        }
    
    else:
        return {
            'scania_code': None,
            'abrams_name': None,
            'description': 'Unknown feature',
            'format': 'unknown'
        }


def print_feature_mapping():
    """Print the complete feature mapping table."""
    print("\n" + "="*80)
    print("M1 ABRAMS TANK SENSOR FEATURE MAPPING")
    print("="*80)
    print(f"{'Scania Code':<15} {'M1 Abrams Name':<30} {'Description':<35}")
    print("-"*80)
    
    for category, features in FEATURE_CATEGORIES.items():
        print(f"\n{category}:")
        print("-"*80)
        for abrams_name in features:
            scania_code = ABRAMS_TO_SCANIA[abrams_name]
            description = FEATURE_DESCRIPTIONS[abrams_name]
            print(f"{scania_code:<15} {abrams_name:<30} {description:<35}")
    
    print("\n" + "="*80)
    print(f"Total Features: {len(ALL_ABRAMS_FEATURES)}")
    print("="*80)


# ============================================================================
# DEMO / TESTING
# ============================================================================

if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║              M1 ABRAMS TANK FEATURE MAPPER - DEMO                            ║
    ║         Bidirectional Mapping: Scania Codes ↔ Military Sensor Names          ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Print mapping table
    print_feature_mapping()
    
    # Demo: Create sample data and convert
    print("\n" + "="*80)
    print("DEMO: Data Format Conversion")
    print("="*80)
    
    # Sample data with Scania codes
    sample_data_scania = {
        'vehicle_id': ['TANK001', 'TANK002'],
        '171_0': [2450, 3100],
        '666_0': [3, 7],
        '427_0': [45, 78],
        '837_0': [120, 200]
    }
    df_scania = pd.DataFrame(sample_data_scania)
    
    print("\nOriginal (Scania format):")
    print(df_scania)
    
    # Convert to Abrams
    df_abrams = rename_features(df_scania, direction='to_abrams')
    print("\nConverted to M1 Abrams format:")
    print(df_abrams)
    
    # Convert back
    df_back = rename_features(df_abrams, direction='to_scania')
    print("\nConverted back to Scania format:")
    print(df_back)
    
    # Validation
    print("\n" + "="*80)
    print("VALIDATION")
    print("="*80)
    
    validation = validate_abrams_data(df_abrams, require_all=False)
    print(f"Abrams format validation: {validation['message']}")
    
    # Feature info
    print("\n" + "="*80)
    print("FEATURE INFORMATION LOOKUP")
    print("="*80)
    
    info = get_feature_info('171_0')
    print(f"\nFeature: {info['scania_code']}")
    print(f"  Display Name: {info['abrams_name']}")
    print(f"  Description: {info['description']}")
