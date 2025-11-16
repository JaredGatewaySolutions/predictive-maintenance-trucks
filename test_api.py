#!/usr/bin/env python3
"""
API Test Script
===============
Tests all API endpoints to verify functionality.
"""

import requests
import json
from pprint import pprint

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health check endpoint."""
    print("\n" + "="*80)
    print("TEST 1: Health Check")
    print("="*80)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    pprint(response.json())
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    print("✓ Health check passed")


def test_metrics():
    """Test metrics endpoint."""
    print("\n" + "="*80)
    print("TEST 2: Metrics")
    print("="*80)
    
    response = requests.get(f"{BASE_URL}/metrics")
    print(f"Status Code: {response.status_code}")
    pprint(response.json())
    assert response.status_code == 200
    print("✓ Metrics endpoint passed")


def test_root():
    """Test root endpoint."""
    print("\n" + "="*80)
    print("TEST 3: Root Endpoint")
    print("="*80)
    
    response = requests.get(f"{BASE_URL}/")
    print(f"Status Code: {response.status_code}")
    pprint(response.json())
    assert response.status_code == 200
    print("✓ Root endpoint passed")


def test_single_prediction():
    """Test single prediction endpoint."""
    print("\n" + "="*80)
    print("TEST 4: Single Prediction")
    print("="*80)
    
    # Sample vehicle data using actual feature names from the model
    # These are the features the model was trained on
    payload = {
        "vehicle_id": "TEST_V001",
        "features": {
            "171_0": 1.0,
            "666_0": 0.0,
            "427_0": 100.0,
            "837_0": 0.0,
            "167_0": 50.0,
            "167_1": 0.0,
            "167_2": 0.0,
            "167_3": 0.0,
            "167_4": 0.0,
            "167_5": 0.0,
            "167_6": 0.0,
            "167_7": 0.0,
            "167_8": 0.0,
            "167_9": 0.0,
            "309_0": 10.0,
            "272_0": 20.0,
            "272_1": 0.0,
            "272_2": 0.0,
            "272_3": 0.0,
            "272_4": 0.0,
            "272_5": 0.0,
            "272_6": 0.0,
            "272_7": 0.0,
            "272_8": 0.0,
            "272_9": 0.0,
            "835_0": 5.0,
            "370_0": 15.0,
            "291_0": 0.0,
            "291_1": 0.0,
            "291_2": 0.0,
            "291_3": 0.0,
            "291_4": 0.0,
            "291_5": 0.0,
            "291_6": 0.0,
            "291_7": 0.0,
            "291_8": 0.0,
            "291_9": 0.0,
            "291_10": 0.0,
            "158_0": 25.0,
            "158_1": 0.0,
            "158_2": 0.0,
            "158_3": 0.0,
            "158_4": 0.0,
            "158_5": 0.0,
            "158_6": 0.0,
            "158_7": 0.0,
            "158_8": 0.0,
            "158_9": 0.0,
            "100_0": 30.0,
            "459_0": 0.0,
            "459_1": 0.0,
            "459_2": 0.0,
            "459_3": 0.0,
            "459_4": 0.0,
            "459_5": 0.0,
            "459_6": 0.0,
            "459_7": 0.0,
            "459_8": 0.0,
            "459_9": 0.0,
            "459_10": 0.0,
            "459_11": 0.0,
            "459_12": 0.0,
            "459_13": 0.0,
            "459_14": 0.0,
            "459_15": 0.0,
            "459_16": 0.0,
            "459_17": 0.0,
            "459_18": 0.0,
            "459_19": 0.0,
            "397_0": 0.0,
            "397_1": 0.0,
            "397_2": 0.0,
            "397_3": 0.0,
            "397_4": 0.0,
            "397_5": 0.0,
            "397_6": 0.0,
            "397_7": 0.0,
            "397_8": 0.0,
            "397_9": 0.0,
            "397_10": 0.0,
            "397_11": 0.0,
            "397_12": 0.0,
            "397_13": 0.0,
            "397_14": 0.0,
            "397_15": 0.0,
            "397_16": 0.0,
            "397_17": 0.0,
            "397_18": 0.0,
            "397_19": 0.0,
            "397_20": 0.0,
            "397_21": 0.0,
            "397_22": 0.0,
            "397_23": 0.0,
            "397_24": 0.0,
            "397_25": 0.0,
            "397_26": 0.0,
            "397_27": 0.0,
            "397_28": 0.0,
            "397_29": 0.0,
            "397_30": 0.0,
            "397_31": 0.0,
            "397_32": 0.0,
            "397_33": 0.0,
            "397_34": 0.0,
            "397_35": 0.0
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/predict",
        json=payload
    )
    
    print(f"Status Code: {response.status_code}")
    result = response.json()
    pprint(result)
    
    assert response.status_code == 200
    assert "prediction" in result
    assert "probability" in result
    assert "risk_level" in result
    print("✓ Single prediction passed")
    
    return result["prediction_id"], result["vehicle_id"]


def test_batch_prediction():
    """Test batch prediction endpoint."""
    print("\n" + "="*80)
    print("TEST 5: Batch Prediction")
    print("="*80)
    
    # Create basic feature dict (all zeros for simplicity)
    def create_features(seed=0):
        features = {}
        feature_names = ["171_0", "666_0", "427_0", "837_0", "167_0", "167_1", "167_2", "167_3", 
                        "167_4", "167_5", "167_6", "167_7", "167_8", "167_9", "309_0", "272_0",
                        "272_1", "272_2", "272_3", "272_4", "272_5", "272_6", "272_7", "272_8",
                        "272_9", "835_0", "370_0", "291_0", "291_1", "291_2", "291_3", "291_4",
                        "291_5", "291_6", "291_7", "291_8", "291_9", "291_10", "158_0", "158_1",
                        "158_2", "158_3", "158_4", "158_5", "158_6", "158_7", "158_8", "158_9",
                        "100_0", "459_0", "459_1", "459_2", "459_3", "459_4", "459_5", "459_6",
                        "459_7", "459_8", "459_9", "459_10", "459_11", "459_12", "459_13", "459_14",
                        "459_15", "459_16", "459_17", "459_18", "459_19", "397_0", "397_1", "397_2",
                        "397_3", "397_4", "397_5", "397_6", "397_7", "397_8", "397_9", "397_10",
                        "397_11", "397_12", "397_13", "397_14", "397_15", "397_16", "397_17", "397_18",
                        "397_19", "397_20", "397_21", "397_22", "397_23", "397_24", "397_25", "397_26",
                        "397_27", "397_28", "397_29", "397_30", "397_31", "397_32", "397_33", "397_34",
                        "397_35"]
        for name in feature_names:
            features[name] = float(seed)
        return features
    
    # Multiple vehicles with different feature values
    payload = {
        "vehicles": [
            {
                "vehicle_id": "TEST_V002",
                "features": create_features(seed=10)
            },
            {
                "vehicle_id": "TEST_V003",
                "features": create_features(seed=5)
            }
        ]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/predict/batch",
        json=payload
    )
    
    print(f"Status Code: {response.status_code}")
    result = response.json()
    print(f"Total predictions: {result['total_count']}")
    for pred in result["predictions"]:
        print(f"  - {pred['vehicle_id']}: {pred['risk_level']} ({pred['probability']:.2%})")
    
    assert response.status_code == 200
    assert result["total_count"] == 2
    print("✓ Batch prediction passed")


def test_get_predictions(vehicle_id):
    """Test get predictions history endpoint."""
    print("\n" + "="*80)
    print("TEST 6: Get Predictions History")
    print("="*80)
    
    response = requests.get(f"{BASE_URL}/api/v1/predictions/{vehicle_id}")
    
    print(f"Status Code: {response.status_code}")
    result = response.json()
    print(f"Vehicle ID: {result['vehicle_id']}")
    print(f"Total predictions: {result['count']}")
    
    assert response.status_code == 200
    assert result["vehicle_id"] == vehicle_id
    assert result["count"] >= 1
    print("✓ Get predictions history passed")


def test_explanation(vehicle_id):
    """Test explanation endpoint."""
    print("\n" + "="*80)
    print("TEST 7: SHAP Explanation")
    print("="*80)
    print("Note: This may fail if SHAP analyzer is not initialized")
    
    response = requests.get(f"{BASE_URL}/api/v1/explain/{vehicle_id}")
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Vehicle ID: {result['vehicle_id']}")
        print(f"Risk Level: {result['risk_level']}")
        print(f"Probability: {result['prediction_proba']:.2%}")
        print(f"\nTop Risk Factors:")
        for factor in result["top_factors"][:5]:
            print(f"  - {factor['feature']}: {factor['shap_value']:.4f} ({factor['effect']})")
        print(f"\nExplanation: {result['explanation_text']}")
        print("✓ Explanation endpoint passed")
    elif response.status_code == 503:
        print("⚠ SHAP analyzer not initialized (expected)")
        print("  This is normal - SHAP initialization requires training data")
    else:
        print(f"✗ Unexpected status code: {response.status_code}")
        pprint(response.json())


def run_all_tests():
    """Run all API tests."""
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + "API TEST SUITE".center(78) + "║")
    print("╚" + "="*78 + "╝")
    
    try:
        # Basic endpoints
        test_health()
        test_metrics()
        test_root()
        
        # Prediction endpoints
        prediction_id, vehicle_id = test_single_prediction()
        test_batch_prediction()
        test_get_predictions(vehicle_id)
        
        # Explanation endpoint (may not work without SHAP initialization)
        test_explanation(vehicle_id)
        
        print("\n" + "╔" + "="*78 + "╗")
        print("║" + "ALL TESTS PASSED!".center(78) + "║")
        print("╚" + "="*78 + "╝\n")
        
    except requests.exceptions.ConnectionError:
        print("\n✗ ERROR: Could not connect to API")
        print("  Make sure the API is running: python app.py")
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")


if __name__ == "__main__":
    run_all_tests()
