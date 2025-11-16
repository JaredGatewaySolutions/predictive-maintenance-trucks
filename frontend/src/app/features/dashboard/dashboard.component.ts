import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatTableModule } from '@angular/material/table';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { RouterLink } from '@angular/router';
import { NgxChartsModule } from '@swimlane/ngx-charts';

import { ApiService } from '../../core/services/api.service';
import { AnalyticsService, RiskSummary, CostAnalysis } from '../../core/services/analytics.service';
import { Prediction } from '../../core/models/prediction.model';
import { ApiMetrics } from '../../core/models/health.model';

@Component({
  selector: 'app-dashboard',
  imports: [
    CommonModule,
    MatCardModule,
    MatTableModule,
    MatProgressSpinnerModule,
    MatIconModule,
    MatButtonModule,
    RouterLink,
    NgxChartsModule
  ],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss'
})
export class DashboardComponent implements OnInit {
  loading = signal(true);
  error = signal<string | null>(null);

  metrics = signal<ApiMetrics | null>(null);
  predictions = signal<Prediction[]>([]);
  riskSummary = signal<RiskSummary | null>(null);
  topRiskVehicles = signal<Prediction[]>([]);
  costAnalysis = signal<CostAnalysis | null>(null);

  // Chart data
  riskChartData = signal<any[]>([]);
  costChartData = signal<any[]>([]);

  displayedColumns = ['vehicle_id', 'risk_level', 'probability', 'timestamp', 'actions'];

  constructor(
    private apiService: ApiService,
    private analyticsService: AnalyticsService
  ) {}

  ngOnInit(): void {
    this.loadDashboardData();
  }

  loadDashboardData(): void {
    this.loading.set(true);
    this.error.set(null);

    // Load metrics from API
    this.apiService.getMetrics().subscribe({
      next: (metrics) => {
        this.metrics.set(metrics);

        // For demo, we'll create sample predictions based on the metrics
        // In production, you'd have an endpoint to get recent predictions
        this.generateSamplePredictions();

        this.loading.set(false);
      },
      error: (err) => {
        this.error.set('Failed to load dashboard data. Please ensure the backend API is running.');
        this.loading.set(false);
        console.error('Dashboard error:', err);
      }
    });
  }

  private generateSamplePredictions(): void {
    // Generate sample prediction data for demonstration
    // In production, this would come from an API endpoint
    const samplePredictions: Prediction[] = [];
    const vehicleCount = 50;

    for (let i = 0; i < vehicleCount; i++) {
      const probability = Math.random();
      let riskLevel: 'HIGH' | 'MEDIUM' | 'LOW';

      if (probability >= 0.7) {
        riskLevel = 'HIGH';
      } else if (probability >= 0.4) {
        riskLevel = 'MEDIUM';
      } else {
        riskLevel = 'LOW';
      }

      samplePredictions.push({
        prediction_id: `pred_${Date.now()}_${i}`,
        vehicle_id: `V${String(1000 + i).padStart(5, '0')}`,
        prediction: probability >= 0.5 ? 1 : 0,
        probability: probability,
        risk_level: riskLevel,
        timestamp: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
        model_version: this.metrics()?.model_version || 'v1'
      });
    }

    this.predictions.set(samplePredictions);
    this.analyzeData(samplePredictions);
  }

  private analyzeData(predictions: Prediction[]): void {
    // Calculate risk summary
    const summary = this.analyticsService.calculateRiskSummary(predictions);
    this.riskSummary.set(summary);

    // Get top risk vehicles
    const topRisk = this.analyticsService.getTopRiskVehicles(predictions, 10);
    this.topRiskVehicles.set(topRisk);

    // Calculate cost analysis
    const costs = this.analyticsService.calculateCostAnalysis(predictions);
    this.costAnalysis.set(costs);

    // Prepare chart data
    this.prepareChartData(summary, costs);
  }

  private prepareChartData(summary: RiskSummary, costs: CostAnalysis): void {
    // Risk distribution chart
    this.riskChartData.set([
      { name: 'High Risk', value: summary.high },
      { name: 'Medium Risk', value: summary.medium },
      { name: 'Low Risk', value: summary.low }
    ]);

    // Cost analysis chart
    this.costChartData.set([
      { name: 'False Positive Cost', value: costs.falsePositiveCost },
      { name: 'False Negative Cost', value: costs.falseNegativeCost },
      { name: 'Savings', value: costs.savings }
    ]);
  }

  getRiskColor(riskLevel: string): string {
    return this.analyticsService.getRiskColor(riskLevel as any);
  }

  formatProbability(probability: number): string {
    return this.analyticsService.formatProbability(probability);
  }

  formatDate(timestamp: string): string {
    return this.analyticsService.formatDate(timestamp);
  }

  refresh(): void {
    this.loadDashboardData();
  }
}
