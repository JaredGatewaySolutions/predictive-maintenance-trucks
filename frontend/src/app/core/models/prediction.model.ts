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

// ============================================================================
// OPTIMAL 20 FEATURES - M1 Abrams Tank Sensor Names
// ============================================================================
// Selected via XGBoost Feature Importance Analysis (Nov 15, 2025)
// These 20 features capture 28.6% of total importance and achieve 92.3% recall

export interface FeatureMetadata {
  code: string;
  displayName: string;
  description: string;
  category: string;
  importance: number;
  rank: number;
  priority: 'highest' | 'high' | 'medium';
}

export const OPTIMAL_FEATURES: FeatureMetadata[] = [
  // System Diagnostics & Performance (Highest Priority)
  {
    code: 'POWER_SYSTEM_METRIC_9',
    displayName: 'Power System Metric 9',
    description: 'Power system performance indicator #9 (Most predictive)',
    category: 'System Diagnostics & Performance',
    importance: 3.41,
    rank: 1,
    priority: 'highest'
  },
  {
    code: 'POWER_SYSTEM_METRIC_5',
    displayName: 'Power System Metric 5',
    description: 'Power system efficiency metric #5',
    category: 'System Diagnostics & Performance',
    importance: 1.71,
    rank: 4,
    priority: 'highest'
  },
  {
    code: 'POWER_SYSTEM_METRIC_6',
    displayName: 'Power System Metric 6',
    description: 'Power distribution and stability metric #6',
    category: 'System Diagnostics & Performance',
    importance: 1.17,
    rank: 18,
    priority: 'highest'
  },

  // Temperature & Environmental Operations
  {
    code: 'TEMP_MODERATE_OPERATIONS',
    displayName: 'Moderate Temp Operations',
    description: 'Operational time in moderate temperature conditions',
    category: 'Temperature & Environmental',
    importance: 1.88,
    rank: 2,
    priority: 'high'
  },
  {
    code: 'TEMP_COLD_OPERATIONS',
    displayName: 'Cold Weather Operations',
    description: 'Operational time in cold weather environments',
    category: 'Temperature & Environmental',
    importance: 1.77,
    rank: 3,
    priority: 'high'
  },
  {
    code: 'TEMP_LOW_OPERATIONS',
    displayName: 'Low Temperature Operations',
    description: 'Performance in low-temperature operations',
    category: 'Temperature & Environmental',
    importance: 1.26,
    rank: 9,
    priority: 'high'
  },

  // Terrain & Mobility
  {
    code: 'TERRAIN_TYPE_4',
    displayName: 'Terrain Type 4',
    description: 'Operations on terrain classification #4',
    category: 'Terrain & Mobility',
    importance: 1.48,
    rank: 5,
    priority: 'medium'
  },
  {
    code: 'TERRAIN_TYPE_1',
    displayName: 'Terrain Type 1',
    description: 'Primary terrain type operational metric',
    category: 'Terrain & Mobility',
    importance: 1.22,
    rank: 13,
    priority: 'medium'
  },
  {
    code: 'TERRAIN_TYPE_5',
    displayName: 'Terrain Type 5',
    description: 'Terrain variation and mobility metric #5',
    category: 'Terrain & Mobility',
    importance: 1.21,
    rank: 15,
    priority: 'medium'
  },

  // Operational Stress & Usage Patterns
  {
    code: 'OPERATIONAL_STRESS_3',
    displayName: 'Operational Stress 3',
    description: 'Operational stress level indicator #3',
    category: 'Operational Stress & Usage',
    importance: 1.34,
    rank: 6,
    priority: 'medium'
  },
  {
    code: 'OPERATIONAL_STRESS_15',
    displayName: 'Operational Stress 15',
    description: 'Extended operational stress metric #15',
    category: 'Operational Stress & Usage',
    importance: 1.29,
    rank: 7,
    priority: 'medium'
  },
  {
    code: 'OPERATIONAL_STRESS_8',
    displayName: 'Operational Stress 8',
    description: 'Stress accumulation pattern #8',
    category: 'Operational Stress & Usage',
    importance: 1.27,
    rank: 8,
    priority: 'medium'
  },
  {
    code: 'OPERATIONAL_STRESS_14',
    displayName: 'Operational Stress 14',
    description: 'Long-term stress indicator #14',
    category: 'Operational Stress & Usage',
    importance: 1.26,
    rank: 10,
    priority: 'medium'
  },
  {
    code: 'OPERATIONAL_STRESS_9',
    displayName: 'Operational Stress 9',
    description: 'Operational intensity metric #9',
    category: 'Operational Stress & Usage',
    importance: 1.17,
    rank: 17,
    priority: 'medium'
  },
  {
    code: 'OPERATIONAL_STRESS_1',
    displayName: 'Operational Stress 1',
    description: 'Base operational stress level',
    category: 'Operational Stress & Usage',
    importance: 1.28,
    rank: 20,
    priority: 'medium'
  },

  // Load & Weight Distribution
  {
    code: 'LOAD_DISTRIBUTION_0',
    displayName: 'Load Distribution 0',
    description: 'Base load distribution metric',
    category: 'Load & Weight Distribution',
    importance: 1.25,
    rank: 11,
    priority: 'medium'
  },
  {
    code: 'LOAD_DISTRIBUTION_2',
    displayName: 'Load Distribution 2',
    description: 'Load pattern and weight distribution #2',
    category: 'Load & Weight Distribution',
    importance: 1.18,
    rank: 16,
    priority: 'medium'
  },
  {
    code: 'LOAD_DISTRIBUTION_4',
    displayName: 'Load Distribution 4',
    description: 'Load variation during operations #4',
    category: 'Load & Weight Distribution',
    importance: 1.12,
    rank: 20,
    priority: 'medium'
  },

  // Component Wear & Degradation
  {
    code: 'COMPONENT_WEAR_33',
    displayName: 'Component Wear 33',
    description: 'Component degradation indicator #33',
    category: 'Component Wear & Degradation',
    importance: 1.23,
    rank: 12,
    priority: 'medium'
  },
  {
    code: 'COMPONENT_WEAR_0',
    displayName: 'Component Wear 0',
    description: 'Base component wear metric',
    category: 'Component Wear & Degradation',
    importance: 1.22,
    rank: 14,
    priority: 'medium'
  },
  {
    code: 'COMPONENT_WEAR_3',
    displayName: 'Component Wear 3',
    description: 'Wear pattern analysis #3',
    category: 'Component Wear & Degradation',
    importance: 1.15,
    rank: 19,
    priority: 'medium'
  }
];

// Feature categories for UI organization
export const FEATURE_CATEGORIES = {
  'System Diagnostics & Performance': ['POWER_SYSTEM_METRIC_9', 'POWER_SYSTEM_METRIC_5', 'POWER_SYSTEM_METRIC_6'],
  'Temperature & Environmental': ['TEMP_MODERATE_OPERATIONS', 'TEMP_COLD_OPERATIONS', 'TEMP_LOW_OPERATIONS'],
  'Operational Stress & Usage': ['OPERATIONAL_STRESS_3', 'OPERATIONAL_STRESS_15', 'OPERATIONAL_STRESS_8', 'OPERATIONAL_STRESS_14', 'OPERATIONAL_STRESS_9', 'OPERATIONAL_STRESS_1'],
  'Load & Weight Distribution': ['LOAD_DISTRIBUTION_0', 'LOAD_DISTRIBUTION_2', 'LOAD_DISTRIBUTION_4'],
  'Terrain & Mobility': ['TERRAIN_TYPE_4', 'TERRAIN_TYPE_1', 'TERRAIN_TYPE_5'],
  'Component Wear & Degradation': ['COMPONENT_WEAR_33', 'COMPONENT_WEAR_0', 'COMPONENT_WEAR_3']
};

// Helper to get all required feature codes
export const REQUIRED_FEATURES = OPTIMAL_FEATURES.map(f => f.code);

// Helper to get feature by code
export function getFeatureMetadata(code: string): FeatureMetadata | undefined {
  return OPTIMAL_FEATURES.find(f => f.code === code);
}
