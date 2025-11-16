// Prediction models based on API response structure

export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH';

export interface Prediction {
  prediction_id: string;
  vehicle_id: string;
  prediction: number;
  probability: number;
  risk_level: RiskLevel;
  timestamp: string;
  model_version: string;
}

export interface PredictionRequest {
  vehicle_id: string;
  features: Record<string, number>;
}

export interface BatchPredictionRequest {
  vehicles: PredictionRequest[];
}

export interface BatchPredictionResponse {
  predictions: Prediction[];
  total_count: number;
  timestamp: string;
}

export interface PredictionHistory {
  vehicle_id: string;
  predictions: Prediction[];
  count: number;
  first_prediction: string;
  last_prediction: string;
}
