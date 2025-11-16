// Health and metrics models

export interface HealthStatus {
  status: string;
  timestamp: string;
  model_loaded: boolean;
  model_version: string;
  uptime_seconds: number;
}

export interface ModelMetrics {
  accuracy: number;
  auc_roc: number;
  cost_savings: number;
  optimal_threshold: number;
  training_samples: number;
  test_samples: number;
}

export interface ApiMetrics {
  model_version: string;
  training_date: string;
  metrics: ModelMetrics;
  predictions_made: number;
  uptime_seconds: number;
}
