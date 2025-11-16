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
  fleet_name?: string;  // Optional fleet name for grouping
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

export interface Fleet {
  fleet_id: string;
  fleet_name: string;
  upload_timestamp: string;
  vehicle_count: number;
  vehicle_ids: string[];
  risk_summary: {
    high: number;
    medium: number;
    low: number;
  };
}

export interface FleetsResponse {
  fleets: Fleet[];
  total_count: number;
}

export interface FleetPredictionsResponse {
  fleet: Fleet;
  predictions: any[];
  total_count: number;
}
