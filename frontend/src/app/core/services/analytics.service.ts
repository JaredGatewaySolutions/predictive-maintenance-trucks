import { Injectable } from '@angular/core';
import { Prediction, RiskLevel } from '../models/prediction.model';

export interface RiskSummary {
  high: number;
  medium: number;
  low: number;
  total: number;
}

export interface ReadinessAnalysis {
  combatReady: number;
  missionCapableLimited: number;
  notMissionCapable: number;
  total: number;
  readinessRate: number; // Percentage of combat ready vehicles
}

@Injectable({
  providedIn: 'root'
})
export class AnalyticsService {
  // Cost constants from the business logic
  private readonly FP_COST = 8;  // False Positive cost
  private readonly FN_COST = 300; // False Negative cost

  constructor() {}

  /**
   * Calculate risk summary from predictions
   */
  calculateRiskSummary(predictions: Prediction[]): RiskSummary {
    const summary: RiskSummary = {
      high: 0,
      medium: 0,
      low: 0,
      total: predictions.length
    };

    predictions.forEach(pred => {
      switch (pred.risk_level) {
        case 'HIGH':
          summary.high++;
          break;
        case 'MEDIUM':
          summary.medium++;
          break;
        case 'LOW':
          summary.low++;
          break;
      }
    });

    return summary;
  }

  /**
   * Get top N high-risk vehicles sorted by probability
   */
  getTopRiskVehicles(predictions: Prediction[], count: number = 10): Prediction[] {
    return [...predictions]
      .filter(p => p.risk_level === 'HIGH' || p.risk_level === 'MEDIUM')
      .sort((a, b) => b.probability - a.probability)
      .slice(0, count);
  }


  /**
   * Get risk level color for UI
   */
  getRiskColor(riskLevel: RiskLevel): string {
    switch (riskLevel) {
      case 'HIGH':
        return '#f44336'; // Red
      case 'MEDIUM':
        return '#CC7722'; // Orange
      case 'LOW':
        return '#4caf50'; // Green
      default:
        return '#B8B8B0'; // Gray
    }
  }

  /**
   * Format probability as percentage
   */
  formatProbability(probability: number): string {
    return `${(probability * 100).toFixed(1)}%`;
  }

  /**
   * Format timestamp to readable date
   */
  formatDate(timestamp: string): string {
    return new Date(timestamp).toLocaleString();
  }
}
