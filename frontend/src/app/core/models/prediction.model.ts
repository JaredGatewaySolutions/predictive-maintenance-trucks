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
// OPTIMAL 20 FEATURES - M1 Abrams Tank Metrics
// ============================================================================
// Based on Army XEM Predictive Maintenance Requirements
// Organized by impact tier on tank availability

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
  // TIER 1: Critical Service Life Limiters (Highest Priority)
  {
    code: 'TRACK_MILES',
    displayName: 'Track Mileage',
    description: 'Cumulative miles on track system - Primary availability driver (6,000 mile rebuild threshold)',
    category: 'Critical Service Life Limiters',
    importance: 5.2,
    rank: 1,
    priority: 'highest'
  },
  {
    code: 'ENGINE_HOURS',
    displayName: 'Engine Operating Hours',
    description: 'Total turbine engine hours - Drives major overhaul scheduling',
    category: 'Critical Service Life Limiters',
    importance: 4.8,
    rank: 2,
    priority: 'highest'
  },
  {
    code: 'MAIN_GUN_ROUNDS',
    displayName: 'Main Gun Round Count',
    description: 'Equivalent Full Charges (EFCs) fired - Gun tube replacement indicator',
    category: 'Critical Service Life Limiters',
    importance: 4.3,
    rank: 3,
    priority: 'highest'
  },

  // TIER 2: High-Failure Subsystems (High Priority)
  {
    code: 'FIRE_CONTROL_SYSTEM_FAULTS',
    displayName: 'Fire Control Faults',
    description: 'Fire control system fault count - High failure rate even in new systems',
    category: 'High-Failure Subsystems',
    importance: 3.9,
    rank: 4,
    priority: 'high'
  },
  {
    code: 'ELECTRICAL_SYSTEM_FAULTS',
    displayName: 'Electrical System Faults',
    description: 'Electrical subsystem failures - Both age-related and initial defects',
    category: 'High-Failure Subsystems',
    importance: 3.7,
    rank: 5,
    priority: 'high'
  },
  {
    code: 'POWERTRAIN_FAILURES',
    displayName: 'Powertrain Failure Count',
    description: 'Transmission and final drive failures - Mission-critical mobility system',
    category: 'High-Failure Subsystems',
    importance: 3.5,
    rank: 6,
    priority: 'high'
  },
  {
    code: 'HYDRAULIC_SYSTEM_FAILURES',
    displayName: 'Hydraulic System Failures',
    description: 'Turret traverse, gun recoil, and brake hydraulic failures',
    category: 'High-Failure Subsystems',
    importance: 3.3,
    rank: 7,
    priority: 'high'
  },

  // TIER 3: Age & Wear Components (Medium-High Priority)
  {
    code: 'ROADWHEEL_ARM_WEAR',
    displayName: 'Roadwheel Arm Wear',
    description: 'Suspension arm degradation - Increases failure probability with age',
    category: 'Age & Wear Components',
    importance: 2.9,
    rank: 8,
    priority: 'medium'
  },
  {
    code: 'TRACK_LINK_WEAR',
    displayName: 'Track Link Wear Index',
    description: 'Track link degradation level - Broken tracks cause immediate immobilization',
    category: 'Age & Wear Components',
    importance: 2.7,
    rank: 9,
    priority: 'medium'
  },
  {
    code: 'TORSION_BAR_DEGRADATION',
    displayName: 'Torsion Bar Degradation',
    description: 'Suspension torsion bar fatigue - Catastrophic collapse risk',
    category: 'Age & Wear Components',
    importance: 2.5,
    rank: 10,
    priority: 'medium'
  },

  // TIER 4: Environmental Stress (Medium Priority)
  {
    code: 'EXTREME_COLD_MILES',
    displayName: 'Extreme Cold Operations',
    description: 'Miles operated below -10°F - Track freezing and electrical failures',
    category: 'Environmental Stress',
    importance: 2.3,
    rank: 11,
    priority: 'medium'
  },
  {
    code: 'EXTREME_HEAT_MILES',
    displayName: 'Extreme Heat Operations',
    description: 'Miles operated above 110°F - Cooling system stress and condensation damage',
    category: 'Environmental Stress',
    importance: 2.2,
    rank: 12,
    priority: 'medium'
  },
  {
    code: 'TERRAIN_SEVERE_MILES',
    displayName: 'Severe Terrain Mileage',
    description: 'Miles on extreme terrain - Maximum stress on all vehicle systems',
    category: 'Environmental Stress',
    importance: 2.1,
    rank: 13,
    priority: 'medium'
  },

  // TIER 5: Operational Factors (Medium Priority)
  {
    code: 'UP_ARMOR_LOAD_HOURS',
    displayName: 'Up-Armor Load Hours',
    description: 'Hours with additional armor (12-15% weight increase) - Fatigue multiplier',
    category: 'Operational Factors',
    importance: 1.9,
    rank: 14,
    priority: 'medium'
  },
  {
    code: 'COMBAT_OPERATIONS_COUNT',
    displayName: 'Combat Operations',
    description: 'Number of high-stress combat maneuvers - Accelerated wear indicator',
    category: 'Operational Factors',
    importance: 1.8,
    rank: 15,
    priority: 'medium'
  },
  {
    code: 'IDLE_HOURS',
    displayName: 'Idle Operating Hours',
    description: 'Turbine hours without movement - Engine wear without productive miles',
    category: 'Operational Factors',
    importance: 1.6,
    rank: 16,
    priority: 'medium'
  },
  {
    code: 'TURRET_SLEW_CYCLES',
    displayName: 'Turret Slew Cycles',
    description: 'Turret rotation cycles - Hydraulic pump and motor wear indicator',
    category: 'Operational Factors',
    importance: 1.5,
    rank: 17,
    priority: 'medium'
  },

  // TIER 6: Diagnostic Indicators (Medium-Low Priority)
  {
    code: 'FAULT_CODES_ACCUMULATED',
    displayName: 'Fault Code Count',
    description: 'Cumulative diagnostic fault codes - Early warning system for failures',
    category: 'Diagnostic Indicators',
    importance: 1.4,
    rank: 18,
    priority: 'medium'
  },
  {
    code: 'TRANSMISSION_TEMP_EVENTS',
    displayName: 'Transmission Overheat Events',
    description: 'Number of transmission overheating incidents - Failure precursor',
    category: 'Diagnostic Indicators',
    importance: 1.3,
    rank: 19,
    priority: 'medium'
  },
  {
    code: 'FUEL_EFFICIENCY_DEGRADATION',
    displayName: 'Fuel Efficiency Loss',
    description: 'Percentage decrease from baseline fuel economy - Engine health indicator',
    category: 'Diagnostic Indicators',
    importance: 1.2,
    rank: 20,
    priority: 'medium'
  }
];

// Feature categories for UI organization
export const FEATURE_CATEGORIES = {
  'Critical Service Life Limiters': ['TRACK_MILES', 'ENGINE_HOURS', 'MAIN_GUN_ROUNDS'],
  'High-Failure Subsystems': ['FIRE_CONTROL_SYSTEM_FAULTS', 'ELECTRICAL_SYSTEM_FAULTS', 'POWERTRAIN_FAILURES', 'HYDRAULIC_SYSTEM_FAILURES'],
  'Age & Wear Components': ['ROADWHEEL_ARM_WEAR', 'TRACK_LINK_WEAR', 'TORSION_BAR_DEGRADATION'],
  'Environmental Stress': ['EXTREME_COLD_MILES', 'EXTREME_HEAT_MILES', 'TERRAIN_SEVERE_MILES'],
  'Operational Factors': ['UP_ARMOR_LOAD_HOURS', 'COMBAT_OPERATIONS_COUNT', 'IDLE_HOURS', 'TURRET_SLEW_CYCLES'],
  'Diagnostic Indicators': ['FAULT_CODES_ACCUMULATED', 'TRANSMISSION_TEMP_EVENTS', 'FUEL_EFFICIENCY_DEGRADATION']
};

// Helper to get all required feature codes
export const REQUIRED_FEATURES = OPTIMAL_FEATURES.map(f => f.code);

// Helper to get feature by code
export function getFeatureMetadata(code: string): FeatureMetadata | undefined {
  return OPTIMAL_FEATURES.find(f => f.code === code);
}

// Helper to get features by category
export function getFeaturesByCategory(category: string): FeatureMetadata[] {
  return OPTIMAL_FEATURES.filter(f => f.category === category);
}

// Helper to get features by priority
export function getFeaturesByPriority(priority: 'highest' | 'high' | 'medium'): FeatureMetadata[] {
  return OPTIMAL_FEATURES.filter(f => f.priority === priority);
}
