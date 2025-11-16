import { Component, OnInit, OnDestroy, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatTableModule } from '@angular/material/table';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { Router, RouterLink } from '@angular/router';
import { NgxChartsModule } from '@swimlane/ngx-charts';
import { Subscription } from 'rxjs';

import { ApiService } from '../../core/services/api.service';
import { AnalyticsService, RiskSummary, CostAnalysis } from '../../core/services/analytics.service';
import { FleetStateService } from '../../core/services/fleet-state.service';
import { Prediction } from '../../core/models/prediction.model';
import { ApiMetrics } from '../../core/models/health.model';
import { Fleet } from '../../core/models/fleet.model';
import { NewAbctDialogComponent } from '../new-abct-dialog/new-abct-dialog.component';

@Component({
  selector: 'app-dashboard',
  imports: [
    CommonModule,
    FormsModule,
    MatCardModule,
    MatTableModule,
    MatProgressSpinnerModule,
    MatIconModule,
    MatButtonModule,
    MatSelectModule,
    MatFormFieldModule,
    MatDialogModule,
    RouterLink,
    NgxChartsModule
  ],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss'
})
export class DashboardComponent implements OnInit, OnDestroy {
  loading = signal(true);
  error = signal<string | null>(null);
  hasNoFleets = signal(false);

  metrics = signal<ApiMetrics | null>(null);
  predictions = signal<Prediction[]>([]);
  riskSummary = signal<RiskSummary | null>(null);
  fleetVehicles = signal<Prediction[]>([]);
  costAnalysis = signal<CostAnalysis | null>(null);

  // Fleet/ABCT management
  fleets = signal<Fleet[]>([]);
  selectedFleet = signal<Fleet | null>(null);
  private fleetsSubscription?: Subscription;
  private selectedFleetSubscription?: Subscription;

  // Chart data
  riskChartData = signal<any[]>([]);
  costChartData = signal<any[]>([]);

  displayedColumns = ['vehicle_id', 'risk_level', 'probability', 'timestamp', 'actions'];

  constructor(
    private apiService: ApiService,
    private analyticsService: AnalyticsService,
    private fleetStateService: FleetStateService,
    private dialog: MatDialog,
    private router: Router
  ) {}

  ngOnInit(): void {
    // Subscribe to fleet state changes
    this.fleetsSubscription = this.fleetStateService.fleets$.subscribe(fleets => {
      this.fleets.set(fleets);
    });

    this.selectedFleetSubscription = this.fleetStateService.selectedFleet$.subscribe(fleet => {
      this.selectedFleet.set(fleet);
      if (fleet) {
        this.loadFleetPredictions(fleet);
      }
    });

    this.loadDashboardData();
  }

  ngOnDestroy(): void {
    this.fleetsSubscription?.unsubscribe();
    this.selectedFleetSubscription?.unsubscribe();
  }

  loadDashboardData(): void {
    this.loading.set(true);
    console.log("loadDashboardData")
    this.error.set(null);

    // Load metrics and fleets
    this.apiService.getMetrics().subscribe({
      next: (metrics) => {
        this.metrics.set(metrics);
        console.log("loadFleets")
        this.loadFleets();
      },
      error: (err) => {
        this.error.set('Failed to load dashboard data. Please ensure the backend API is running.');
        this.loading.set(false);
        console.error('Dashboard error:', err);
      }
    });
  }

  loadFleets(): void {
    this.apiService.getFleets().subscribe({
      next: (response) => {
        console.log(response);
        this.fleetStateService.setFleets(response.fleets || []);

        // If no fleet selected and fleets exist, select the first one
        if (!this.selectedFleet() && response.fleets && response.fleets.length > 0) {
          this.hasNoFleets.set(false);
          this.fleetStateService.setSelectedFleet(response.fleets[0]);
        } else if (!response.fleets || response.fleets.length === 0) {
          // No fleets available - show empty state
          this.hasNoFleets.set(true);
          this.clearDashboardData();
        }

        this.loading.set(false);
      },
      error: (err) => {
        console.error('Error loading fleets:', err);
        this.error.set('Failed to load ABCTs. Please try again.');
        this.loading.set(false);
      }
    });
  }

  selectFleet(fleet: Fleet): void {
    this.fleetStateService.setSelectedFleet(fleet);
  }

  loadFleetPredictions(fleet: Fleet): void {
    this.loading.set(true);

    // Load predictions for this fleet
    this.apiService.getFleetPredictions(fleet.fleet_id).subscribe({
      next: (response) => {
        const predictions: Prediction[] = response.predictions.map((p: any) => ({
          prediction_id: p.prediction_id,
          vehicle_id: p.vehicle_id,
          prediction: p.prediction,
          probability: p.probability,
          risk_level: p.risk_level,
          timestamp: p.timestamp,
          model_version: p.model_version
        }));

        this.predictions.set(predictions);
        this.analyzeData(predictions);
        this.loading.set(false);
      },
      error: (err) => {
        console.error('Error loading fleet predictions:', err);
        this.error.set(`Failed to load predictions for ABCT: ${fleet.fleet_name}`);
        this.loading.set(false);
      }
    });
  }

  private clearDashboardData(): void {
    // Clear all prediction data when no fleets are available
    this.predictions.set([]);
    this.riskSummary.set(null);
    this.fleetVehicles.set([]);
    this.costAnalysis.set(null);
    this.riskChartData.set([]);
    this.costChartData.set([]);
  }

  private analyzeData(predictions: Prediction[]): void {
    // Calculate risk summary
    const summary = this.analyticsService.calculateRiskSummary(predictions);
    this.riskSummary.set(summary);

    // Sort all vehicles by risk: high first, then by probability
    const sortedVehicles = [...predictions].sort((a, b) => {
      const riskOrder = { 'High': 0, 'Medium': 1, 'Low': 2 };
      const riskCompare = riskOrder[a.risk_level as keyof typeof riskOrder] - riskOrder[b.risk_level as keyof typeof riskOrder];
      if (riskCompare !== 0) return riskCompare;
      return b.probability - a.probability; // Higher probability first
    });
    this.fleetVehicles.set(sortedVehicles);

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

  navigateToVehicle(vehicle: Prediction): void {
    this.router.navigate(['/vehicle', vehicle.vehicle_id]);
  }
}
