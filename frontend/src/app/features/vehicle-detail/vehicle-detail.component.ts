import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTableModule } from '@angular/material/table';
import { NgxChartsModule } from '@swimlane/ngx-charts';

import { ApiService } from '../../core/services/api.service';
import { AnalyticsService } from '../../core/services/analytics.service';
import { Prediction, PredictionHistory } from '../../core/models/prediction.model';
import { Explanation, ShapFactor } from '../../core/models/explanation.model';

@Component({
  selector: 'app-vehicle-detail',
  imports: [
    CommonModule,
    RouterLink,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatTableModule,
    NgxChartsModule
  ],
  templateUrl: './vehicle-detail.component.html',
  styleUrl: './vehicle-detail.component.scss'
})
export class VehicleDetailComponent implements OnInit {
  vehicleId = signal<string>('');
  loading = signal(true);
  error = signal<string | null>(null);

  prediction = signal<Prediction | null>(null);
  explanation = signal<Explanation | null>(null);
  history = signal<PredictionHistory | null>(null);

  shapChartData = signal<any[]>([]);
  displayedColumns = ['feature', 'value', 'shap_value', 'effect'];

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private apiService: ApiService,
    public analyticsService: AnalyticsService
  ) {}

  ngOnInit(): void {
    this.route.params.subscribe(params => {
      const id = params['id'];
      if (id) {
        this.vehicleId.set(id);
        this.loadVehicleData(id);
      }
    });
  }

  loadVehicleData(vehicleId: string): void {
    this.loading.set(true);
    this.error.set(null);

    // Load prediction history
    this.apiService.getPredictionHistory(vehicleId).subscribe({
      next: (history) => {
        this.history.set(history);
        if (history.predictions && history.predictions.length > 0) {
          // Use the most recent prediction
          this.prediction.set(history.predictions[0]);
        }

        // Try to load explanation
        this.loadExplanation(vehicleId);
      },
      error: (err) => {
        // If no history found, show error but allow manual prediction
        console.warn('No prediction history found:', err);
        this.error.set('No prediction data found for this vehicle. You can make a prediction from the batch upload page.');
        this.loading.set(false);
      }
    });
  }

  loadExplanation(vehicleId: string): void {
    this.apiService.getExplanation(vehicleId).subscribe({
      next: (explanation) => {
        this.explanation.set(explanation);
        this.prepareShapChart(explanation.top_factors);
        this.loading.set(false);
      },
      error: (err) => {
        console.warn('SHAP explanation not available:', err);
        this.loading.set(false);
      }
    });
  }

  prepareShapChart(factors: ShapFactor[]): void {
    // Prepare bar chart data for SHAP values
    const chartData = factors.map(factor => ({
      name: factor.feature,
      value: Math.abs(factor.shap_value),
      extra: {
        effect: factor.effect,
        actualValue: factor.shap_value
      }
    }));

    this.shapChartData.set(chartData);
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

  goBack(): void {
    this.router.navigate(['/dashboard']);
  }
}
