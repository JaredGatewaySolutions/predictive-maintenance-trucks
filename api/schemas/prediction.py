"""
Prediction Request/Response Schemas
====================================
Pydantic models for prediction endpoints - M1 Abrams Tank Edition.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class VehicleFeatures(BaseModel):
    """
    M1 Abrams Tank Sensor Data - OPTIMAL 20 FEATURES ONLY.
    Based on Army XEM Predictive Maintenance Requirements.
    These 20 features achieve high predictive accuracy for tank availability.

    Organized by impact tier:
    - TIER 1: Critical Service Life Limiters
    - TIER 2: High-Failure Subsystems
    - TIER 3: Age & Wear Components
    - TIER 4: Environmental Stress
    - TIER 5: Operational Factors
    - TIER 6: Diagnostic Indicators
    """

    # TIER 1: Critical Service Life Limiters (Highest Priority)
    TRACK_MILES: Optional[float] = Field(
        None,
        description="Track Mileage - Primary availability driver (6,000 mile rebuild threshold) - Rank 1",
    )
    ENGINE_HOURS: Optional[float] = Field(
        None,
        description="Engine Operating Hours - Turbine hours driving major overhaul scheduling - Rank 2",
    )
    MAIN_GUN_ROUNDS: Optional[float] = Field(
        None,
        description="Main Gun Round Count - Equivalent Full Charges (EFCs) for gun tube replacement - Rank 3",
    )

    # TIER 2: High-Failure Subsystems
    FIRE_CONTROL_SYSTEM_FAULTS: Optional[float] = Field(
        None,
        description="Fire Control Faults - High failure rate even in new systems - Rank 4",
    )
    ELECTRICAL_SYSTEM_FAULTS: Optional[float] = Field(
        None,
        description="Electrical System Faults - Both age-related and initial defects - Rank 5",
    )
    POWERTRAIN_FAILURES: Optional[float] = Field(
        None,
        description="Powertrain Failure Count - Transmission and final drive failures - Rank 6",
    )
    HYDRAULIC_SYSTEM_FAILURES: Optional[float] = Field(
        None,
        description="Hydraulic System Failures - Turret traverse, gun recoil, brake failures - Rank 7",
    )

    # TIER 3: Age & Wear Components
    ROADWHEEL_ARM_WEAR: Optional[float] = Field(
        None,
        description="Roadwheel Arm Wear - Suspension arm degradation increases with age - Rank 8",
    )
    TRACK_LINK_WEAR: Optional[float] = Field(
        None,
        description="Track Link Wear Index - Broken tracks cause immediate immobilization - Rank 9",
    )
    TORSION_BAR_DEGRADATION: Optional[float] = Field(
        None,
        description="Torsion Bar Degradation - Suspension fatigue and catastrophic collapse risk - Rank 10",
    )

    # TIER 4: Environmental Stress
    EXTREME_COLD_MILES: Optional[float] = Field(
        None,
        description="Extreme Cold Operations - Miles below -10°F causing track freezing - Rank 11",
    )
    EXTREME_HEAT_MILES: Optional[float] = Field(
        None,
        description="Extreme Heat Operations - Miles above 110°F stressing cooling systems - Rank 12",
    )
    TERRAIN_SEVERE_MILES: Optional[float] = Field(
        None,
        description="Severe Terrain Mileage - Miles on extreme terrain stressing all systems - Rank 13",
    )

    # TIER 5: Operational Factors
    UP_ARMOR_LOAD_HOURS: Optional[float] = Field(
        None,
        description="Up-Armor Load Hours - Hours with 12-15% additional weight (fatigue multiplier) - Rank 14",
    )
    COMBAT_OPERATIONS_COUNT: Optional[float] = Field(
        None,
        description="Combat Operations - Number of high-stress combat maneuvers - Rank 15",
    )
    IDLE_HOURS: Optional[float] = Field(
        None,
        description="Idle Operating Hours - Turbine hours without movement (unproductive wear) - Rank 16",
    )
    TURRET_SLEW_CYCLES: Optional[float] = Field(
        None,
        description="Turret Slew Cycles - Turret rotation cycles wearing hydraulic systems - Rank 17",
    )

    # TIER 6: Diagnostic Indicators
    FAULT_CODES_ACCUMULATED: Optional[float] = Field(
        None,
        description="Fault Code Count - Cumulative diagnostic codes as early warning - Rank 18",
    )
    TRANSMISSION_TEMP_EVENTS: Optional[float] = Field(
        None,
        description="Transmission Overheat Events - Overheating incidents as failure precursor - Rank 19",
    )
    FUEL_EFFICIENCY_DEGRADATION: Optional[float] = Field(
        None,
        description="Fuel Efficiency Loss - Percentage decrease from baseline (engine health) - Rank 20",
    )

    class Config:
        extra = "forbid"  # Reject extra fields - we only want these 20!
        schema_extra = {
            "example": {
                "TRACK_MILES": 1250.5,
                "ENGINE_HOURS": 980.3,
                "MAIN_GUN_ROUNDS": 710.8,
                "FIRE_CONTROL_SYSTEM_FAULTS": 850.2,
                "ELECTRICAL_SYSTEM_FAULTS": 420.1,
                "POWERTRAIN_FAILURES": 310.2,
                "HYDRAULIC_SYSTEM_FAILURES": 650.0,
                "ROADWHEEL_ARM_WEAR": 890.4,
                "TRACK_LINK_WEAR": 430.2,
                "TORSION_BAR_DEGRADATION": 340.7,
                "EXTREME_COLD_MILES": 220.4,
                "EXTREME_HEAT_MILES": 180.5,
                "TERRAIN_SEVERE_MILES": 150.3,
                "UP_ARMOR_LOAD_HOURS": 95.3,
                "COMBAT_OPERATIONS_COUNT": 125.8,
                "IDLE_HOURS": 500.1,
                "TURRET_SLEW_CYCLES": 380.6,
                "FAULT_CODES_ACCUMULATED": 290.7,
                "TRANSMISSION_TEMP_EVENTS": 45.8,
                "FUEL_EFFICIENCY_DEGRADATION": 68.4,
            }
        }


class SinglePredictionRequest(BaseModel):
    """
    Request for single vehicle prediction.
    """

    vehicle_id: Optional[str] = Field(
        None, description="Vehicle identifier (e.g., TANK001)"
    )
    features: Dict[str, Any] = Field(
        ..., description="Vehicle features (20 tank metrics)"
    )

    class Config:
        schema_extra = {
            "example": {
                "vehicle_id": "TANK001",
                "features": {
                    "TRACK_MILES": 1250.5,
                    "ENGINE_HOURS": 980.3,
                    "MAIN_GUN_ROUNDS": 710.8,
                    "FIRE_CONTROL_SYSTEM_FAULTS": 850.2,
                    "ELECTRICAL_SYSTEM_FAULTS": 420.1,
                    "POWERTRAIN_FAILURES": 310.2,
                    "HYDRAULIC_SYSTEM_FAILURES": 650.0,
                    "ROADWHEEL_ARM_WEAR": 890.4,
                    "TRACK_LINK_WEAR": 430.2,
                    "TORSION_BAR_DEGRADATION": 340.7,
                    "EXTREME_COLD_MILES": 220.4,
                    "EXTREME_HEAT_MILES": 180.5,
                    "TERRAIN_SEVERE_MILES": 150.3,
                    "UP_ARMOR_LOAD_HOURS": 95.3,
                    "COMBAT_OPERATIONS_COUNT": 125.8,
                    "IDLE_HOURS": 500.1,
                    "TURRET_SLEW_CYCLES": 380.6,
                    "FAULT_CODES_ACCUMULATED": 290.7,
                    "TRANSMISSION_TEMP_EVENTS": 45.8,
                    "FUEL_EFFICIENCY_DEGRADATION": 68.4,
                },
            }
        }


class BatchPredictionRequest(BaseModel):
    """
    Request for batch predictions on multiple vehicles.
    Useful for fleet-level analysis across ABCTs.
    """

    vehicles: List[SinglePredictionRequest] = Field(
        ..., description="List of vehicles to predict"
    )
    fleet_name: Optional[str] = Field(
        None,
        description="Optional fleet name for grouping (e.g., '1ABCT_1CD_Ironhorse')",
    )

    class Config:
        schema_extra = {
            "example": {
                "vehicles": [
                    {
                        "vehicle_id": "TANK001",
                        "features": {
                            "TRACK_MILES": 1250.5,
                            "ENGINE_HOURS": 980.3,
                            "MAIN_GUN_ROUNDS": 710.8,
                            "FIRE_CONTROL_SYSTEM_FAULTS": 850.2,
                            "ELECTRICAL_SYSTEM_FAULTS": 420.1,
                            "POWERTRAIN_FAILURES": 310.2,
                            "HYDRAULIC_SYSTEM_FAILURES": 650.0,
                            "ROADWHEEL_ARM_WEAR": 890.4,
                            "TRACK_LINK_WEAR": 430.2,
                            "TORSION_BAR_DEGRADATION": 340.7,
                            "EXTREME_COLD_MILES": 220.4,
                            "EXTREME_HEAT_MILES": 180.5,
                            "TERRAIN_SEVERE_MILES": 150.3,
                            "UP_ARMOR_LOAD_HOURS": 95.3,
                            "COMBAT_OPERATIONS_COUNT": 125.8,
                            "IDLE_HOURS": 500.1,
                            "TURRET_SLEW_CYCLES": 380.6,
                            "FAULT_CODES_ACCUMULATED": 290.7,
                            "TRANSMISSION_TEMP_EVENTS": 45.8,
                            "FUEL_EFFICIENCY_DEGRADATION": 68.4,
                        },
                    },
                    {
                        "vehicle_id": "TANK002",
                        "features": {
                            "TRACK_MILES": 1380.2,
                            "ENGINE_HOURS": 1050.1,
                            "MAIN_GUN_ROUNDS": 780.3,
                            "FIRE_CONTROL_SYSTEM_FAULTS": 920.5,
                            "ELECTRICAL_SYSTEM_FAULTS": 450.8,
                            "POWERTRAIN_FAILURES": 340.5,
                            "HYDRAULIC_SYSTEM_FAILURES": 710.3,
                            "ROADWHEEL_ARM_WEAR": 950.2,
                            "TRACK_LINK_WEAR": 470.8,
                            "TORSION_BAR_DEGRADATION": 390.2,
                            "EXTREME_COLD_MILES": 250.1,
                            "EXTREME_HEAT_MILES": 200.3,
                            "TERRAIN_SEVERE_MILES": 170.2,
                            "UP_ARMOR_LOAD_HOURS": 105.1,
                            "COMBAT_OPERATIONS_COUNT": 138.5,
                            "IDLE_HOURS": 550.4,
                            "TURRET_SLEW_CYCLES": 410.2,
                            "FAULT_CODES_ACCUMULATED": 320.5,
                            "TRANSMISSION_TEMP_EVENTS": 52.1,
                            "FUEL_EFFICIENCY_DEGRADATION": 75.2,
                        },
                    },
                ],
                "fleet_name": "1ABCT_1CD_Ironhorse",
            }
        }


class PredictionResponse(BaseModel):
    """
    Response for single prediction.
    """

    prediction_id: str = Field(..., description="Unique prediction identifier")
    vehicle_id: Optional[str] = Field(None, description="Vehicle identifier")
    prediction: int = Field(
        ..., description="Prediction class (0=operational, 1=failure_risk)"
    )
    probability: float = Field(..., description="Failure probability (0.0-1.0)")
    risk_level: str = Field(
        ..., description="Risk level: HIGH (>0.7), MEDIUM (0.3-0.7), or LOW (<0.3)"
    )
    timestamp: str = Field(..., description="Prediction timestamp (ISO 8601)")
    model_version: str = Field(..., description="Model version used")

    class Config:
        schema_extra = {
            "example": {
                "prediction_id": "pred_20251116_120000_abc123",
                "vehicle_id": "TANK001",
                "prediction": 1,
                "probability": 0.85,
                "risk_level": "HIGH",
                "timestamp": "2025-11-16T12:00:00.123456",
                "model_version": "m1_abrams_v1_20251116",
            }
        }


class BatchPredictionResponse(BaseModel):
    """
    Response for batch predictions.
    """

    predictions: List[PredictionResponse] = Field(
        ..., description="List of predictions"
    )
    total_count: int = Field(..., description="Total number of predictions")
    timestamp: str = Field(..., description="Batch processing timestamp")
    fleet_name: Optional[str] = Field(None, description="Fleet name if provided")

    class Config:
        schema_extra = {
            "example": {
                "predictions": [
                    {
                        "prediction_id": "pred_20251116_120000_abc123",
                        "vehicle_id": "TANK001",
                        "prediction": 1,
                        "probability": 0.85,
                        "risk_level": "HIGH",
                        "timestamp": "2025-11-16T12:00:00.123456",
                        "model_version": "m1_abrams_v1_20251116",
                    },
                    {
                        "prediction_id": "pred_20251116_120000_def456",
                        "vehicle_id": "TANK002",
                        "prediction": 0,
                        "probability": 0.15,
                        "risk_level": "LOW",
                        "timestamp": "2025-11-16T12:00:00.234567",
                        "model_version": "m1_abrams_v1_20251116",
                    },
                ],
                "total_count": 2,
                "timestamp": "2025-11-16T12:00:00.123456",
                "fleet_name": "1ABCT_1CD_Ironhorse",
            }
        }


class PredictionHistory(BaseModel):
    """
    Historical predictions for a vehicle.
    """

    vehicle_id: str = Field(..., description="Vehicle identifier")
    predictions: List[PredictionResponse] = Field(..., description="Past predictions")
    count: int = Field(..., description="Number of predictions")
    first_prediction: Optional[str] = Field(
        None, description="First prediction timestamp"
    )
    last_prediction: Optional[str] = Field(
        None, description="Last prediction timestamp"
    )

    class Config:
        schema_extra = {
            "example": {
                "vehicle_id": "TANK001",
                "predictions": [
                    {
                        "prediction_id": "pred_20251116_120000_abc123",
                        "vehicle_id": "TANK001",
                        "prediction": 1,
                        "probability": 0.85,
                        "risk_level": "HIGH",
                        "timestamp": "2025-11-16T12:00:00.123456",
                        "model_version": "m1_abrams_v1_20251116",
                    }
                ],
                "count": 1,
                "first_prediction": "2025-11-16T12:00:00.123456",
                "last_prediction": "2025-11-16T12:00:00.123456",
            }
        }


class FleetSummary(BaseModel):
    """
    Summary statistics for a fleet of vehicles.
    """

    fleet_id: str = Field(..., description="Fleet identifier")
    fleet_name: str = Field(..., description="Fleet name (e.g., '1ABCT_1CD_Ironhorse')")
    upload_timestamp: str = Field(..., description="When fleet was uploaded")
    vehicle_count: int = Field(..., description="Number of vehicles in fleet")
    vehicle_ids: List[str] = Field(..., description="List of vehicle IDs")
    risk_summary: Dict[str, int] = Field(
        ..., description="Count of vehicles by risk level"
    )

    class Config:
        schema_extra = {
            "example": {
                "fleet_id": "fleet_1abct_20251116",
                "fleet_name": "1ABCT_1CD_Ironhorse",
                "upload_timestamp": "2025-11-16T12:00:00.123456",
                "vehicle_count": 87,
                "vehicle_ids": ["TANK001", "TANK002", "TANK003"],
                "risk_summary": {"HIGH": 12, "MEDIUM": 35, "LOW": 40},
            }
        }


class FleetsResponse(BaseModel):
    """
    Response listing all fleets.
    """

    fleets: List[FleetSummary] = Field(..., description="List of fleet summaries")
    total_count: int = Field(..., description="Total number of fleets")

    class Config:
        schema_extra = {
            "example": {
                "fleets": [
                    {
                        "fleet_id": "fleet_1abct_20251116",
                        "fleet_name": "1ABCT_1CD_Ironhorse",
                        "upload_timestamp": "2025-11-16T12:00:00.123456",
                        "vehicle_count": 87,
                        "vehicle_ids": ["TANK001", "TANK002"],
                        "risk_summary": {"HIGH": 12, "MEDIUM": 35, "LOW": 40},
                    }
                ],
                "total_count": 1,
            }
        }


class FleetPredictionsResponse(BaseModel):
    """
    Response with all predictions for a specific fleet.
    """

    fleet: FleetSummary = Field(..., description="Fleet information")
    predictions: List[PredictionResponse] = Field(
        ..., description="All predictions for this fleet"
    )
    total_count: int = Field(..., description="Total number of predictions")

    class Config:
        schema_extra = {
            "example": {
                "fleet": {
                    "fleet_id": "fleet_1abct_20251116",
                    "fleet_name": "1ABCT_1CD_Ironhorse",
                    "upload_timestamp": "2025-11-16T12:00:00.123456",
                    "vehicle_count": 87,
                    "vehicle_ids": ["TANK001", "TANK002"],
                    "risk_summary": {"HIGH": 12, "MEDIUM": 35, "LOW": 40},
                },
                "predictions": [
                    {
                        "prediction_id": "pred_20251116_120000_abc123",
                        "vehicle_id": "TANK001",
                        "prediction": 1,
                        "probability": 0.85,
                        "risk_level": "HIGH",
                        "timestamp": "2025-11-16T12:00:00.123456",
                        "model_version": "m1_abrams_v1_20251116",
                    }
                ],
                "total_count": 1,
            }
        }
