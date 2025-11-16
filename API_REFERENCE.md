# API Reference - Predictive Maintenance API

## Overview

REST API for vehicle failure predictions with SHAP explanations.

**Base URL:** `http://localhost:8000`
**Documentation:** `http://localhost:8000/docs`
**Interactive API Docs:** `http://localhost:8000/redoc`

---

## Endpoints

### Health & Monitoring

#### GET /health

Health check endpoint for monitoring and load balancers.

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2025-11-15T18:03:48.434439",
  "model_loaded": true,
  "model_version": "v2_20251115_173803",
  "uptime_seconds": 12.75
}
```

#### GET /metrics

Model performance metrics and API statistics.

**Response:**

```json
{
  "model_version": "v2_20251115_173803",
  "training_date": "2025-11-15T17:38:03.499637",
  "metrics": {
    "accuracy": 0.91,
    "auc_roc": 0.6416361416361416,
    "cost_savings": 1032.0,
    "optimal_threshold": 0.1,
    "training_samples": 800,
    "test_samples": 200
  },
  "predictions_made": 127,
  "uptime_seconds": 3600.5
}
```

---

### Predictions

#### POST /api/v1/predict

Single vehicle prediction.

**Request:**

```json
{
  "vehicle_id": "V12345",
  "features": {
    "171_0": 1.0,
    "666_0": 0.0,
    "427_0": 100.0,
    // ... all 106 features
  }
}
```

**Response:**

```json
{
  "prediction_id": "pred_20251115_180354_219a456e",
  "vehicle_id": "V12345",
  "prediction": 0,
  "probability": 0.0789,
  "risk_level": "LOW",
  "timestamp": "2025-11-15T18:03:54.639628",
  "model_version": "v2_20251115_173803"
}
```

**Risk Levels:**

- `LOW`: probability < 0.4
- `MEDIUM`: 0.4 ≤ probability < 0.7
- `HIGH`: probability ≥ 0.7

#### POST /api/v1/predict/batch

Batch predictions for multiple vehicles.

**Request:**

```json
{
  "vehicles": [
    {
      "vehicle_id": "V001",
      "features": { /* feature dict */ }
    },
    {
      "vehicle_id": "V002",
      "features": { /* feature dict */ }
    }
  ]
}
```

**Response:**

```json
{
  "predictions": [
    {
      "prediction_id": "pred_...",
      "vehicle_id": "V001",
      "prediction": 0,
      "probability": 0.08,
      "risk_level": "LOW",
      "timestamp": "2025-11-15T18:03:54.639628",
      "model_version": "v2_20251115_173803"
    }
  ],
  "total_count": 2,
  "timestamp": "2025-11-15T18:03:54.639628"
}
```

#### GET /api/v1/predictions/{vehicle_id}

Retrieve past predictions for a vehicle.

**Response:**

```json
{
  "vehicle_id": "V12345",
  "predictions": [
    {
      "prediction_id": "pred_...",
      "vehicle_id": "V12345",
      "prediction": 0,
      "probability": 0.08,
      "risk_level": "LOW",
      "timestamp": "2025-11-15T18:03:54.639628",
      "model_version": "v2_20251115_173803"
    }
  ],
  "count": 1,
  "first_prediction": "2025-11-15T18:03:54.639628",
  "last_prediction": "2025-11-15T18:03:54.639628"
}
```

---

### Explanations

#### GET /api/v1/explain/{vehicle_id}

Generate SHAP explanation for a vehicle's prediction.

**Note:** Requires SHAP analyzer initialization (may return 503 if not initialized).

**Response:**

```json
{
  "vehicle_id": "V12345",
  "prediction_id": "pred_...",
  "prediction_proba": 0.85,
  "risk_level": "HIGH",
  "top_factors": [
    {
      "feature": "427_0",
      "value": 100.0,
      "shap_value": 0.123,
      "effect": "INCREASES"
    },
    {
      "feature": "666_0",
      "value": 0.0,
      "shap_value": -0.045,
      "effect": "DECREASES"
    }
  ],
  "explanation_text": "Primary risk driver: 427_0 (contributes +0.123 to failure risk)",
  "timestamp": "2025-11-15T18:03:54.639628"
}
```

---

## Starting the API

```bash
# Start the API server
python app.py

# Or with uvicorn directly
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

The API will:

1. Load the latest trained model from `data/models/current/`
2. Initialize application state
3. Start listening on `http://0.0.0.0:8000`

---

## Testing

```bash
# Run the test suite
python test_api.py
```

This will test all endpoints:

- ✓ Health check
- ✓ Metrics
- ✓ Root endpoint
- ✓ Single prediction
- ✓ Batch prediction
- ✓ Prediction history
- ⚠ SHAP explanation (may not work without initialized analyzer)

---

## Features Supported

The model currently expects **106 features**:

```text
171_0, 666_0, 427_0, 837_0, 167_0 through 167_9,
309_0, 272_0 through 272_9, 835_0, 370_0,
291_0 through 291_10, 158_0 through 158_9, 100_0,
459_0 through 459_19, 397_0 through 397_35
```

All features should be included in the prediction request. The API handles missing features gracefully.

---

## Error Codes

- `200`: Success
- `400`: Bad Request (invalid input format)
- `404`: Not Found (vehicle_id doesn't exist)
- `422`: Unprocessable Entity (validation errors)
- `500`: Internal Server Error (model/prediction failures)
- `503`: Service Unavailable (model not loaded or SHAP not initialized)

---

## CORS

CORS is enabled for all origins in development. Update `app.py` for production:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],  # Restrict in production
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

---

## Data Storage

Predictions are saved to `data/predictions/`:

- `{vehicle_id}.json` - All predictions for a vehicle
- `{prediction_id}.json` - Individual prediction records

---

## Next Steps

1. **Initialize SHAP at startup** - Load training data to enable explanations
2. **Add authentication** - Implement API key or JWT authentication
3. **Rate limiting** - Prevent abuse with rate limits
4. **Logging** - Enhanced logging for production monitoring
5. **Caching** - Cache predictions for frequently queried vehicles
6. **Database** - Replace JSON files with proper database (PostgreSQL/MongoDB)

---

## Production Deployment

### Docker

```bash
# Build image
docker build -t predictive-maintenance-api .

# Run container
docker run -p 8000:8000 predictive-maintenance-api
```

### Kubernetes

Deploy using Kubernetes manifests for scalability and high availability.

### Cloud Options

- **AWS**: Deploy on ECS/Fargate or Lambda
- **Azure**: Deploy on App Service or Container Instances
- **GCP**: Deploy on Cloud Run or GKE

---

## Support

For issues or questions:

- Check the interactive docs: `http://localhost:8000/docs`
- Review logs in the terminal
- Check `data/predictions/` for stored predictions
