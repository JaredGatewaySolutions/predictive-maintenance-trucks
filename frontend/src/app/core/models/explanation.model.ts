// Explanation and SHAP models

export type FeatureEffect = 'INCREASES' | 'DECREASES';

export interface ShapFactor {
  feature: string;
  description?: string;
  value: number;
  shap_value: number;
  effect: FeatureEffect;
}

export interface Explanation {
  vehicle_id: string;
  prediction_id: string;
  prediction_proba: number;
  risk_level: string;
  top_factors: ShapFactor[];
  explanation_text: string;
  timestamp: string;
}
