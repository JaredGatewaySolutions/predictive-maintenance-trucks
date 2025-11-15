# Predictive Maintenance - Fullstack Architecture

## 🏗️ Project Structure

```text
predictive-maintenance-trucks/
├── app.py                          # [FUTURE] FastAPI application entry point
├── requirements.txt                # Python dependencies
├── test_pipeline.py               # Pipeline testing script
│
├── core/                          # ✅ COMPLETED - Core ML business logic
│   ├── __init__.py                # Module exports
│   ├── scania_loader.py           # Data ingestion from SCANIA dataset
│   ├── risk_predictor.py          # XGBoost-based failure prediction
│   ├── explainability_analyzer.py # SHAP-based explanations
│   ├── pipeline.py                # TrainingPipeline & PredictionPipeline
│   └── model_manager.py           # Model persistence & versioning
│
├── api/                           # [FUTURE] REST API layer
│   ├── __init__.py
│   ├── routes/
│   │   ├── predictions.py         # POST /predict, GET /predictions
│   │   ├── explanations.py        # GET /explain/{vehicle_id}
│   │   ├── models.py              # GET /models, POST /train
│   │   └── health.py              # GET /health, GET /metrics
│   ├── schemas/
│   │   ├── prediction.py          # Pydantic models
│   │   └── vehicle.py
│   └── middleware/
│       ├── auth.py
│       └── logging.py
│
├── frontend/                      # ✅ CREATED - Angular app placeholder
│   └── README.md                  # Implementation guide
│
├── data/                          # ✅ COMPLETED - Data storage
│   ├── README.md                  # Data structure documentation
│   ├── raw/                       # Original SCANIA CSV files (existing)
│   ├── processed/                 # Preprocessed data
│   ├── models/                    # Trained model artifacts
│   │   ├── registry.json          # Model registry
│   │   ├── current/               # Current production model
│   │   └── v1_YYYYMMDD_HHMMSS/   # Versioned models
│   ├── predictions/               # Prediction results (JSON)
│   └── cache/                     # Cached SHAP values
│
├── tests/                         # [FUTURE] Unit & integration tests
├── scripts/                       # [FUTURE] Utility scripts
└── docs/                          # Existing documentation
```

## 📦 Core Module Architecture (✅ COMPLETED)

### 1. `core/pipeline.py`

**Purpose**: Orchestrates end-to-end ML workflows

**Classes**:

- `TrainingPipeline`: Complete training workflow
  - Load data → Train model → Evaluate → Save with versioning
  - Method: `run_full_pipeline()` - One-line training
  
- `PredictionPipeline`: Inference for new data
  - Load model → Make predictions → Categorize risk (HIGH/MEDIUM/LOW)
  - Methods: `predict_single()`, `predict_batch()`

**Usage**:

```python
# Training
from core.pipeline import TrainingPipeline
pipeline = TrainingPipeline()
results = pipeline.run_full_pipeline(n_samples=5000)

# Prediction
from core.pipeline import PredictionPipeline
pipeline = PredictionPipeline()
pipeline.load_model()
prediction = pipeline.predict_single(vehicle_data)
```

### 2. `core/model_manager.py`

**Purpose**: Model persistence and versioning

**Features**:

- Automatic versioning with timestamps (e.g., `v1_20251115_173242`)
- JSON-based model registry
- Save/load models with metadata
- Filesystem-based (no database required)

**Directory Structure**:

```text
data/models/
├── registry.json              # All models with metrics
├── current/                   # Symlink to latest model
│   ├── model.pkl
│   └── metadata.json
└── v1_20251115_173242/       # Versioned models
    ├── model.pkl
    └── metadata.json
```

**Usage**:

```python
from core.model_manager import ModelManager

manager = ModelManager()
manager.save_model(predictor, metadata)
loaded = manager.load_latest_model()
```

### 3. Existing Modules (Moved to `core/`)

- `scania_loader.py`: Data ingestion ✅
- `risk_predictor.py`: XGBoost model with cost-sensitive learning ✅
- `explainability_analyzer.py`: SHAP explanations ✅

## 🔄 Workflow: Training vs. Serving

### Training (Offline - Run Once or Scheduled)

```text
┌─────────────────────────────────────────────────────┐
│  scripts/train_model.py or test_pipeline.py        │
│                                                     │
│  1. TrainingPipeline.run_full_pipeline()           │
│     ↓                                               │
│  2. Load data from data/raw/                       │
│     ↓                                               │
│  3. Train XGBoost model                            │
│     ↓                                               │
│  4. Evaluate & calculate cost savings              │
│     ↓                                               │
│  5. ModelManager.save_model()                      │
│     ↓                                               │
│  6. Model saved to data/models/v1_TIMESTAMP/       │
└─────────────────────────────────────────────────────┘
```

### Serving (Online - Always Running)

```text
┌─────────────────────────────────────────────────────┐
│  app.py (FastAPI) - [FUTURE]                       │
│                                                     │
│  On startup:                                        │
│  1. PredictionPipeline.load_model()                │
│     ↓                                               │
│  2. Model loaded from data/models/current/         │
│                                                     │
│  Per request:                                       │
│  3. POST /api/v1/predict                           │
│     ↓                                               │
│  4. pipeline.predict_single(vehicle_data)          │
│     ↓                                               │
│  5. Return JSON response with risk level           │
└─────────────────────────────────────────────────────┘
```

## 🎯 Microservices Architecture

### Current Status: **Monolithic Core** ✅

- All ML logic in `core/` package
- Easy to refactor into microservices later

### Future Microservices Design

```text
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  Training        │     │  Prediction      │     │  Explanation     │
│  Service         │     │  Service         │     │  Service         │
│  (core.pipeline) │     │  (core.pipeline) │     │  (core.analyzer) │
│                  │     │                  │     │                  │
│  Train models    │     │  Load model      │     │  Load model      │
│  Save to disk    │     │  Make predictions│     │  Generate SHAP   │
└──────────────────┘     └──────────────────┘     └──────────────────┘
         │                        │                         │
         └────────────────────────┼─────────────────────────┘
                                  ▼
                    ┌─────────────────────────┐
                    │  Shared File System     │
                    │  data/models/           │
                    │  (or S3/Azure Blob)     │
                    └─────────────────────────┘
```

## 📊 Data Flow: JSON-Based Persistence

### Model Metadata Example

```json
{
  "version": "v1_20251115_173242",
  "model_type": "RiskPredictor",
  "training_date": "2025-11-15T17:32:42.995757",
  "metrics": {
    "accuracy": 0.900,
    "auc_roc": 0.703,
    "recall": 0.000,
    "precision": 0.000
  },
  "training_samples": 800,
  "test_samples": 200,
  "optimal_threshold": 0.10,
  "cost_savings": 2388.0
}
```

### Prediction Result Example

```json
{
  "prediction_id": "pred_20251115_173242_abc123",
  "timestamp": "2025-11-15T17:32:45.123456",
  "model_version": "v1_20251115_173242",
  "vehicle_id": "12345",
  "prediction": 1,
  "probability": 0.85,
  "risk_level": "HIGH"
}
```

## 🚀 Next Steps

### Phase 1: Core ✅ COMPLETED

- [x] Create `core/` folder structure
- [x] Implement `model_manager.py`
- [x] Implement `pipeline.py`
- [x] Move existing modules to `core/`
- [x] Create `data/` subfolders
- [x] Test pipeline functionality

### Phase 2: API Layer (NEXT)

- [ ] Create `api/` folder structure
- [ ] Implement FastAPI application (`app.py`)
- [ ] Create prediction endpoints
- [ ] Create explanation endpoints
- [ ] Add health check endpoints
- [ ] Test API with Postman/curl

### Phase 3: Frontend

- [ ] Initialize Angular project in `frontend/`
- [ ] Create dashboard component
- [ ] Create vehicle detail view
- [ ] Implement API service for backend calls
- [ ] Add charts for cost analysis

### Phase 4: Deployment

- [ ] Dockerize API and frontend
- [ ] Create Docker Compose setup
- [ ] Add CI/CD pipeline
- [ ] Deploy to cloud (AWS/Azure)

## 🔧 Development Commands

### Test Core Pipeline

```bash
python test_pipeline.py
```

### Train New Model

```python
from core.pipeline import TrainingPipeline
pipeline = TrainingPipeline()
results = pipeline.run_full_pipeline(
    n_samples=None,  # Use all data
    test_size=0.2,
    initialize_shap=True,
    save_model=True
)
```

### Load and Use Model

```python
from core.pipeline import PredictionPipeline
pipeline = PredictionPipeline()
pipeline.load_model()  # Loads latest
prediction = pipeline.predict_single(vehicle_data)
```

### List All Models

```python
from core.model_manager import ModelManager
manager = ModelManager()
models = manager.list_models()
for model in models:
    print(f"{model['version']}: AUC-ROC = {model['metrics']['auc_roc']}")
```

## 📝 Key Design Decisions

### 1. **Filesystem-based persistence** (No database yet)

- ✅ Simpler to start with
- ✅ Easy to migrate to S3/Azure Blob later
- ✅ JSON for metadata, pickle for models

### 2. **Microservices-ready monolith**

- ✅ All logic in `core/` package
- ✅ Easy to split into services later
- ✅ Shared model storage on filesystem

### 3. **Separate training from serving**

- ✅ Train offline (scripts/cron jobs)
- ✅ API loads pre-trained models (fast)
- ✅ No training during API requests

### 4. **Angular for frontend**

- ✅ Enterprise-grade framework
- ✅ TypeScript for type safety
- ✅ Material Design UI components

## 🎓 Architecture Benefits

1. **Separation of Concerns**: Core ML logic independent of API/UI
2. **Versioning**: Every model saved with timestamp and metrics
3. **Reproducibility**: Metadata tracks training params and data
4. **Scalability**: Easy to add more services or scale horizontally
5. **Testability**: Each component can be tested independently
6. **Maintainability**: Clear structure, well-documented modules

---

**Status**: ✅ Core pipeline complete and tested!  
**Next**: Build API layer with FastAPI
