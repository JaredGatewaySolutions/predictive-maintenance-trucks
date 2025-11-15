# Frontend - Predictive Maintenance Dashboard

This directory will contain the Angular frontend application.

## Future Implementation

The frontend will be built using **Angular** and will include:

### Features

- **Fleet Dashboard**: Overview of all vehicles with risk scores
- **Vehicle Detail View**: Individual vehicle analysis with SHAP explanations
- **Cost Analysis**: Visual representation of maintenance cost savings
- **Batch Upload**: Upload CSV files for batch predictions
- **Model Metrics**: Display current model performance

### Components (Planned)

```text
frontend/
├── src/
│   ├── app/
│   │   ├── components/
│   │   │   ├── dashboard/
│   │   │   ├── vehicle-detail/
│   │   │   ├── cost-analysis/
│   │   │   ├── batch-upload/
│   │   │   └── model-metrics/
│   │   ├── services/
│   │   │   ├── api.service.ts
│   │   │   ├── prediction.service.ts
│   │   │   └── auth.service.ts
│   │   ├── models/
│   │   └── app.module.ts
│   ├── assets/
│   └── environments/
├── angular.json
├── package.json
└── tsconfig.json
```

### Technology Stack

- **Framework**: Angular 15+
- **UI Library**: Angular Material / Bootstrap
- **Charts**: Chart.js or D3.js for visualizations
- **State Management**: NgRx (if needed)
- **HTTP Client**: Angular HttpClient for API calls

### API Integration

The frontend will connect to the FastAPI backend at:

- `http://localhost:8000/api/v1/`

### Development

Once implemented, start the dev server with:

```bash
cd frontend
npm install
ng serve
```

---

**Status**: 📦 Placeholder - To be implemented

For now, focus on completing the **core/** modules and **API** layer.
