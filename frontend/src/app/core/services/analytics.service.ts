import { Injectable } from '@angular/core';
import { Prediction, RiskLevel } from '../models/prediction.model';

export interface RiskSummary {
  high: number;
  medium: number;
  low: number;
  total: number;
}

export interface CostAnalysis {
  falsePositiveCost: number;
  falseNegativeCost: number;
  totalCost: number;
  savings: number;
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
   * Calculate cost analysis
   * This is a simplified estimation based on the model's cost-sensitive learning
   */
  calculateCostAnalysis(predictions: Prediction[], actualFailures?: number[]): CostAnalysis {
    // Estimated false positives (vehicles marked high risk but won't fail)
    const highRiskCount = predictions.filter(p => p.risk_level === 'HIGH').length;

    // Estimated false negatives (vehicles marked low risk but will fail)
    // Using a conservative estimate based on typical model performance
    const lowRiskCount = predictions.filter(p => p.risk_level === 'LOW').length;
    const estimatedFN = Math.round(lowRiskCount * 0.05); // ~5% miss rate

    const falsePositiveCost = highRiskCount * this.FP_COST;
    const falseNegativeCost = estimatedFN * this.FN_COST;
    const totalCost = falsePositiveCost + falseNegativeCost;

    // Estimate savings compared to no prediction system
    // Assume without system, all failures would be missed
    const worstCaseCost = predictions.length * 0.1 * this.FN_COST; // 10% failure rate
    const savings = Math.max(0, worstCaseCost - totalCost);

    return {
      falsePositiveCost,
      falseNegativeCost,
      totalCost,
      savings
    };
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
