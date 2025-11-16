# Predictive Maintenance Frontend

Angular 20 frontend application for the predictive maintenance system.

## Overview

This frontend provides an intuitive dashboard for fleet managers to:

- Monitor vehicle risk levels in real-time
- View detailed predictions with SHAP explanations
- Upload CSV files for batch predictions
- Analyze cost savings from predictive maintenance

## Technology Stack

- **Framework**: Angular 20 (standalone components)
- **UI Library**: Angular Material
- **Charts**: ngx-charts (Swimlane)
- **CSV Parsing**: PapaParse
- **HTTP**: Angular HttpClient
- **State Management**: Angular Signals

## Features

### 1. Dashboard (`/dashboard`)

- **Fleet Risk Overview**: High/Medium/Low risk counts
- **Model Performance Metrics**: Accuracy, AUC-ROC, cost savings
- **Top 10 High-Risk Vehicles**: Sorted by failure probability
- **Risk Distribution Chart**: Pie chart showing risk breakdown
- **Cost Analysis Chart**: Bar chart showing FP/FN costs and savings

### 2. Vehicle Detail View (`/vehicle/:id`)

- **Risk Score Display**: Large, color-coded risk gauge
- **Prediction Details**: Model version, prediction class, probability
- **SHAP Explanation**: Why is this vehicle at risk?
- **Feature Importance**: Bar chart and table of top contributing features
- **Prediction History**: Timeline of past predictions

### 3. Batch Upload (`/upload`)

- **CSV File Upload**: Drag-and-drop or file select
- **Batch Processing**: Upload multiple vehicles at once
- **Results Table**: View all predictions with filtering
- **Export Results**: Download predictions as CSV
- **Format Guide**: Clear documentation of required CSV format

## Project Structure

```text
frontend/
├── src/
│   ├── app/
│   │   ├── core/                      # Core services & models
│   │   │   ├── models/
│   │   │   │   ├── prediction.model.ts
│   │   │   │   ├── health.model.ts
│   │   │   │   └── explanation.model.ts
│   │   │   └── services/
│   │   │       ├── api.service.ts     # HTTP client wrapper
│   │   │       └── analytics.service.ts
│   │   │
│   │   ├── features/                  # Feature modules
│   │   │   ├── dashboard/
│   │   │   ├── vehicle-detail/
│   │   │   └── batch-upload/
│   │   │
│   │   ├── app.component.ts           # Root component
│   │   ├── app.routes.ts              # Route configuration
│   │   └── app.config.ts              # App configuration
│   │
│   ├── environments/
│   │   ├── environment.ts             # Dev config
│   │   └── environment.prod.ts        # Prod config
│   │
│   └── styles.scss                    # Global styles
│
├── angular.json                       # Angular CLI config
├── package.json                       # Dependencies
└── README.md
```

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Angular CLI 20
- Backend API running on `http://localhost:8000`

### Installation

```bash
cd frontend
npm install
```

### Development Server

```bash
npm start
# or
ng serve
```

Navigate to `http://localhost:4200/`. The app will automatically reload if you change any source files.

### Build

```bash
npm run build
# or
ng build
```

The build artifacts will be stored in the `dist/` directory.

### Production Build

```bash
ng build --configuration production
```

## Configuration

### API URL

Update the API URL in environment files:

**Development** (`src/environments/environment.ts`):

```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000'
};
```

**Production** (`src/environments/environment.prod.ts`):

```typescript
export const environment = {
  production: true,
  apiUrl: 'https://your-api-domain.com'
};
```

## API Integration

The frontend connects to these backend endpoints:

- `GET /health` - Health check
- `GET /metrics` - Model performance metrics
- `POST /api/v1/predict` - Single vehicle prediction
- `POST /api/v1/predict/batch` - Batch predictions
- `GET /api/v1/predictions/{vehicle_id}` - Prediction history
- `GET /api/v1/explain/{vehicle_id}` - SHAP explanation

## Usage

### Start Backend API

```bash
# In the root directory
python app.py
```

The API should be running on `http://localhost:8000`

### Start Frontend

```bash
# In the frontend directory
npm start
```

Navigate to `http://localhost:4200/`

### Making Predictions

1. **View Dashboard**: See overall fleet status
2. **Click on Vehicle**: View detailed risk analysis
3. **Upload CSV**: Process multiple vehicles at once

### CSV Format for Batch Upload

```csv
vehicle_id,171_0,666_0,427_0,837_0,...
V00001,76294,0,5,120,...
V00002,85321,1,3,115,...
```

- First row: column headers
- `vehicle_id`: Optional (auto-generated if missing)
- Other columns: Numeric feature values (106 features expected)

## Deployment

### Using Nginx (Recommended)

- Build the application:

```bash
ng build --configuration production
```

- Copy `dist/predictive-maintenance-frontend/browser/*` to Nginx web root

- Configure Nginx:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /var/www/html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### Docker

Create `Dockerfile` in frontend directory:

```dockerfile
FROM node:18 AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build -- --configuration production

FROM nginx:alpine
COPY --from=build /app/dist/predictive-maintenance-frontend/browser /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

Build and run:

```bash
docker build -t predictive-maintenance-frontend .
docker run -p 80:80 predictive-maintenance-frontend
```

## Troubleshooting

### CORS Issues

If you encounter CORS errors:

1. Ensure backend has CORS configured for frontend URL
2. Check `app.py` has correct `allow_origins` in CORS middleware

### API Connection Failed

1. Verify backend is running: `curl http://localhost:8000/health`
2. Check environment configuration in `environment.ts`
3. Open browser DevTools → Network tab to see failed requests

### Charts Not Displaying

1. Ensure ngx-charts is properly installed: `npm install @swimlane/ngx-charts`
2. Check browser console for errors
3. Verify data format matches chart expectations

## Development

### Generate New Component

```bash
ng generate component features/my-component --skip-tests
```

### Generate New Service

```bash
ng generate service core/services/my-service --skip-tests
```

### Code Style

- Use Angular Signals for state management
- Follow standalone component pattern
- Use SCSS for styling
- Use Material Design components
- Keep components focused and reusable

## Contributing

1. Follow Angular style guide
2. Write meaningful commit messages
3. Test thoroughly before submitting
4. Update documentation as needed

## Future Enhancements

- [ ] Real-time updates via WebSocket
- [ ] Advanced filtering and search
- [ ] User authentication
- [ ] Model version comparison
- [ ] Custom alert thresholds
- [ ] Export reports as PDF
- [ ] Dark mode theme

## License

See main project LICENSE file.

## Support

For issues or questions, please refer to the main project documentation.

---
