# Data Directory Structure

This directory contains all data-related files for the predictive maintenance system.

## Directory Structure

```text
data/
├── raw/                    # Original SCANIA CSV files (existing)
│   ├── aps_failure_training_set.csv
│   └── aps_failure_test_set.csv
│
├── processed/              # Preprocessed and cleaned data
│   ├── training_data.csv
│   ├── test_data.csv
│   └── feature_engineering_notes.json
│
├── models/                 # Trained model artifacts
│   ├── registry.json      # Model registry (versions, metadata)
│   ├── current/           # Current production model
│   │   ├── model.pkl
│   │   ├── metadata.json
│   │   └── scaler.pkl (optional)
│   ├── v1_20251115_132045/  # Versioned models
│   │   ├── model.pkl
│   │   ├── metadata.json
│   │   └── scaler.pkl
│   └── v2_20251115_154523/
│       └── ...
│
├── predictions/            # Prediction results (JSON files)
│   ├── batch_predictions_20251115_132045.json
│   ├── vehicle_12345_prediction.json
│   └── ...
│
└── cache/                  # Cached computations (SHAP values, etc.)
    ├── shap_values_v1.pkl
    └── feature_importance_v1.json
```

## File Formats

### Predictions JSON Format

```json
{
  "prediction_id": "pred_20251115_132045_abc123",
  "timestamp": "2025-11-15T13:20:45.123456",
  "model_version": "v1_20251115_132045",
  "vehicle_id": "12345",
  "prediction": 1,
  "probability": 0.85,
  "risk_level": "HIGH",
  "features": {
    "aa_000": 76294,
    "ab_000": 0,
    ...
  },
  "explanation": {
    "top_features": [
      {"feature": "aa_000", "impact": 0.12},
      {"feature": "ab_000", "impact": -0.08}
    ]
  }
}
```

### Model Metadata JSON Format

```json
{
  "version": "v1_20251115_132045",
  "model_type": "RiskPredictor",
  "training_date": "2025-11-15T13:20:45.123456",
  "pipeline_version": "1.0",
  "metrics": {
    "accuracy": 0.95,
    "auc_roc": 0.97,
    "recall": 0.89,
    "precision": 0.92
  },
  "training_samples": 40000,
  "test_samples": 10000,
  "features": ["aa_000", "ab_000", ...],
  "optimal_threshold": 0.35,
  "cost_savings": 12000,
  "handle_imbalance": true,
  "calibrate_probabilities": true
}
```

## Usage

### Saving Predictions

```python
from datetime import datetime
import json
from pathlib import Path

prediction_result = {
    "prediction_id": f"pred_{datetime.now().strftime('%Y%m%d_%H%M%S')}_abc123",
    "timestamp": datetime.now().isoformat(),
    "vehicle_id": "12345",
    "prediction": 1,
    "probability": 0.85,
    "risk_level": "HIGH"
}

# Save to file
output_path = Path("data/predictions") / f"vehicle_{prediction_result['vehicle_id']}_prediction.json"
with open(output_path, 'w') as f:
    json.dump(prediction_result, f, indent=2)
```

### Loading Models

```python
from core.model_manager import ModelManager

manager = ModelManager(models_dir="data/models")
loaded = manager.load_latest_model()

predictor = loaded['model']
metadata = loaded['metadata']
```

## Backup & Versioning

- **Models**: All models are automatically versioned by timestamp
- **Predictions**: Keep predictions for audit trail and model retraining
- **Raw Data**: Never modify raw data; always work with copies in `processed/`

## Data Privacy

⚠️ **Important**:

- Add `data/predictions/*.json` to `.gitignore` if containing sensitive data
- Consider encryption for production deployments
- Implement data retention policies

---

**Note**: The `raw/` subdirectory already exists with SCANIA dataset. Other directories are created as needed.
