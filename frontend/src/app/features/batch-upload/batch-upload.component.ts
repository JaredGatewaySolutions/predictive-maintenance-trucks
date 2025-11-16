import { Component, signal, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatTableModule } from '@angular/material/table';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { RouterLink } from '@angular/router';
import { Subscription } from 'rxjs';
import * as Papa from 'papaparse';

import { ApiService } from '../../core/services/api.service';
import { AnalyticsService } from '../../core/services/analytics.service';
import { FleetStateService } from '../../core/services/fleet-state.service';
import { Prediction, BatchPredictionRequest, OPTIMAL_FEATURES, FEATURE_CATEGORIES, REQUIRED_FEATURES } from '../../core/models/prediction.model';
import { Fleet } from '../../core/models/fleet.model';
import { NewAbctDialogComponent } from '../new-abct-dialog/new-abct-dialog.component';

@Component({
  selector: 'app-batch-upload',
  imports: [
    CommonModule,
    RouterLink,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatProgressBarModule,
    MatTableModule,
    MatInputModule,
    MatFormFieldModule,
    MatSelectModule,
    MatDialogModule,
    FormsModule
  ],
  templateUrl: './batch-upload.component.html',
  styleUrl: './batch-upload.component.scss'
})
export class BatchUploadComponent implements OnInit, OnDestroy {
  uploading = signal(false);
  processing = signal(false);
  error = signal<string | null>(null);
  success = signal<string | null>(null);

  uploadedFile = signal<File | null>(null);
  abctName = signal<string>('');
  predictions = signal<Prediction[]>([]);

  // Fleet/ABCT management
  fleets = signal<Fleet[]>([]);
  selectedFleet = signal<Fleet | null>(null);
  private fleetsSubscription?: Subscription;
  private selectedFleetSubscription?: Subscription;

  displayedColumns = ['vehicle_id', 'risk_level', 'probability', 'prediction', 'actions'];

  // Feature categories for display
  // Feature categories for display
  featureCategoriesArray = [
    {
      name: 'Critical Service Life Limiters',
      features: FEATURE_CATEGORIES['Critical Service Life Limiters'],
      priority: 'highest',
      icon: 'warning'  // or 'priority_high'
    },
    {
      name: 'High-Failure Subsystems',
      features: FEATURE_CATEGORIES['High-Failure Subsystems'],
      priority: 'high',
      icon: 'error_outline'  // or 'report_problem'
    },
    {
      name: 'Age & Wear Components',
      features: FEATURE_CATEGORIES['Age & Wear Components'],
      priority: 'medium',
      icon: 'build'  // or 'engineering'
    },
    {
      name: 'Environmental Stress',
      features: FEATURE_CATEGORIES['Environmental Stress'],
      priority: 'medium',
      icon: 'thermostat'  // or 'wb_sunny'
    },
    {
      name: 'Operational Factors',
      features: FEATURE_CATEGORIES['Operational Factors'],
      priority: 'medium',
      icon: 'speed'  // or 'military_tech'
    },
    {
      name: 'Diagnostic Indicators',
      features: FEATURE_CATEGORIES['Diagnostic Indicators'],
      priority: 'medium',
      icon: 'analytics'  // or 'troubleshoot'
    }
  ];

  constructor(
    private apiService: ApiService,
    public analyticsService: AnalyticsService,
    private fleetStateService: FleetStateService,
    private dialog: MatDialog
  ) { }

  ngOnInit(): void {
    // Subscribe to fleet state changes
    this.fleetsSubscription = this.fleetStateService.fleets$.subscribe(fleets => {
      this.fleets.set(fleets);
    });

    this.selectedFleetSubscription = this.fleetStateService.selectedFleet$.subscribe(fleet => {
      this.selectedFleet.set(fleet);
      if (fleet) {
        this.abctName.set(fleet.fleet_name);
      }
    });

    // Load fleets
    this.loadFleets();
  }

  ngOnDestroy(): void {
    this.fleetsSubscription?.unsubscribe();
    this.selectedFleetSubscription?.unsubscribe();
  }

  loadFleets(): void {
    this.apiService.getFleets().subscribe({
      next: (response) => {
        this.fleetStateService.setFleets(response.fleets || []);
      },
      error: (err) => {
        console.error('Error loading fleets:', err);
      }
    });
  }

  onFleetSelected(fleet: Fleet): void {
    this.fleetStateService.setSelectedFleet(fleet);
    this.abctName.set(fleet.fleet_name);
  }

  openNewAbctDialog(): void {
    const dialogRef = this.dialog.open(NewAbctDialogComponent, {
      width: '500px',
      disableClose: true
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        // User entered an ABCT name - just set it, the fleet will be created when CSV is uploaded
        console.log('Setting new ABCT name:', result);
        this.abctName.set(result);
        this.selectedFleet.set(null); // Clear selection since this is a new fleet
        this.success.set(`ABCT name set to "${result}". Upload a CSV file to create the fleet.`);
      }
    });
  }

  getFeatureDescription(featureName: string): string {
    const feature = OPTIMAL_FEATURES.find(f => f.code === featureName);
    return feature ? `${feature.displayName}: ${feature.description} (Importance: ${feature.importance}%)` : featureName;
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      const file = input.files[0];

      // Validate file type
      if (!file.name.endsWith('.csv')) {
        this.error.set('Please select a CSV file');
        return;
      }

      this.uploadedFile.set(file);
      // Set default ABCT name to filename (without extension) if none selected
      if (!this.abctName()) {
        this.abctName.set(file.name.replace('.csv', ''));
      }
      this.error.set(null);
      this.success.set(null);
      this.predictions.set([]);
    }
  }

  processCSV(): void {
    const file = this.uploadedFile();
    if (!file) {
      this.error.set('Please select a file first');
      return;
    }

    const abctNameValue = this.abctName().trim();
    if (!abctNameValue) {
      this.error.set('ABCT name is required. Please select an existing ABCT or create a new one.');
      return;
    }

    this.processing.set(true);
    this.error.set(null);
    this.success.set(null);

    // Parse CSV file
    Papa.parse(file, {
      header: true,
      dynamicTyping: true,
      skipEmptyLines: true,
      complete: (results) => {
        this.handleParsedCSV(results.data);
      },
      error: (error) => {
        this.error.set(`CSV parsing error: ${error.message}`);
        this.processing.set(false);
      }
    });
  }

  private handleParsedCSV(data: any[]): void {
    if (!data || data.length === 0) {
      this.error.set('CSV file is empty');
      this.processing.set(false);
      return;
    }

    console.log(`📊 Parsed ${data.length} rows from CSV`);
    console.log('Sample row:', data[0]);

    // Validate CSV has required features
    const csvColumns = Object.keys(data[0]);
    const missingFeatures = REQUIRED_FEATURES.filter(feature => !csvColumns.includes(feature));

    if (missingFeatures.length > 0) {
      console.warn('⚠️ Missing required features:', missingFeatures);
      this.error.set(
        `CSV is missing ${missingFeatures.length} required features. ` +
        `Missing: ${missingFeatures.slice(0, 5).join(', ')}${missingFeatures.length > 5 ? '...' : ''}. ` +
        `Please download the template above for the correct format.`
      );
      this.processing.set(false);
      return;
    }

    console.log('✅ All 20 required features found in CSV');

    // Convert CSV data to batch prediction request
    const batchRequest: BatchPredictionRequest = {
      vehicles: data.map((row, index) => {
        // Extract vehicle_id if present, otherwise generate one
        const vehicleId = row.vehicle_id || row.VehicleID || row.tank_id || `V${String(index + 1).padStart(5, '0')}`;

        // Extract features (all numeric columns except vehicle_id)
        const features: Record<string, number> = {};
        Object.keys(row).forEach(key => {
          if (key !== 'vehicle_id' && key !== 'VehicleID' && key !== 'tank_id' && typeof row[key] === 'number') {
            features[key] = row[key];
          }
        });

        return {
          vehicle_id: vehicleId,
          features: features
        };
      }),
      fleet_name: this.abctName()  // ABCT name is now required
    };

    console.log(`🚀 Sending batch request with ${batchRequest.vehicles.length} vehicles`);
    console.log(`Features in first vehicle: ${Object.keys(batchRequest.vehicles[0].features).length}`);
    console.log('Feature names:', Object.keys(batchRequest.vehicles[0].features).slice(0, 5));

    // Send batch prediction request
    this.apiService.predictBatch(batchRequest).subscribe({
      next: (response) => {
        console.log(`✅ Received ${response.total_count} predictions`);
        this.predictions.set(response.predictions);
        this.success.set(`Successfully processed ${response.total_count} vehicles for ABCT: ${this.abctName()}`);
        this.processing.set(false);

        // Reload fleets to get the newly created/updated fleet
        this.loadFleets();
      },
      error: (err) => {
        console.error('❌ Batch prediction error:', err);

        // Extract detailed error message
        let errorMessage = 'Prediction failed';
        if (err.error && err.error.detail) {
          errorMessage = err.error.detail;
        } else if (err.message) {
          errorMessage = err.message;
        }

        this.error.set(`Prediction error: ${errorMessage}`);
        this.processing.set(false);
      }
    });
  }

  downloadResults(): void {
    const predictions = this.predictions();
    if (predictions.length === 0) {
      return;
    }

    // Convert predictions to CSV
    const csv = Papa.unparse(predictions.map(p => ({
      vehicle_id: p.vehicle_id,
      prediction: p.prediction,
      probability: p.probability,
      risk_level: p.risk_level,
      timestamp: p.timestamp,
      model_version: p.model_version,
      prediction_id: p.prediction_id
    })));

    // Download file
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `predictions_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
    window.URL.revokeObjectURL(url);
  }

  clearResults(): void {
    this.uploadedFile.set(null);
    this.predictions.set([]);
    this.error.set(null);
    this.success.set(null);

    // Don't clear ABCT name or selection - keep it for next upload

    // Reset file input
    const fileInput = document.getElementById('csvFileInput') as HTMLInputElement;
    if (fileInput) {
      fileInput.value = '';
    }
  }

  reprocessCurrentFleet(): void {
    const fleet = this.selectedFleet();
    const file = this.uploadedFile();

    if (!fleet) {
      this.error.set('Please select an ABCT to reprocess');
      return;
    }

    if (!file) {
      this.error.set('Please select a CSV file to reprocess the ABCT');
      return;
    }

    this.processing.set(true);
    this.error.set(null);

    // Parse CSV and send reprocess request
    Papa.parse(file, {
      header: true,
      dynamicTyping: true,
      skipEmptyLines: true,
      complete: (results) => {
        this.apiService.reprocessFleet({
          fleet_id: fleet.fleet_id,
          csv_data: results.data
        }).subscribe({
          next: (response) => {
            this.success.set(`Successfully reprocessed ABCT: ${fleet.fleet_name}`);
            this.processing.set(false);
            this.loadFleets();
          },
          error: (err) => {
            this.error.set(`Failed to reprocess ABCT: ${err.message}`);
            this.processing.set(false);
          }
        });
      },
      error: (error) => {
        this.error.set(`CSV parsing error: ${error.message}`);
        this.processing.set(false);
      }
    });
  }

  getRiskColor(riskLevel: string): string {
    return this.analyticsService.getRiskColor(riskLevel as any);
  }

  formatProbability(probability: number): string {
    return this.analyticsService.formatProbability(probability);
  }

  getHighRiskCount(): number {
    return this.predictions().filter(p => p.risk_level === 'HIGH').length;
  }

  getMediumRiskCount(): number {
    return this.predictions().filter(p => p.risk_level === 'MEDIUM').length;
  }

  getLowRiskCount(): number {
    return this.predictions().filter(p => p.risk_level === 'LOW').length;
  }
}
