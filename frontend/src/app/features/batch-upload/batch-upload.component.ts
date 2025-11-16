import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatTableModule } from '@angular/material/table';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { RouterLink } from '@angular/router';
import * as Papa from 'papaparse';

import { ApiService } from '../../core/services/api.service';
import { AnalyticsService } from '../../core/services/analytics.service';
import { Prediction, BatchPredictionRequest } from '../../core/models/prediction.model';

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
    FormsModule
  ],
  templateUrl: './batch-upload.component.html',
  styleUrl: './batch-upload.component.scss'
})
export class BatchUploadComponent {
  uploading = signal(false);
  processing = signal(false);
  error = signal<string | null>(null);
  success = signal<string | null>(null);

  uploadedFile = signal<File | null>(null);
  fleetName = signal<string>('');
  predictions = signal<Prediction[]>([]);

  displayedColumns = ['vehicle_id', 'risk_level', 'probability', 'prediction', 'actions'];

  constructor(
    private apiService: ApiService,
    public analyticsService: AnalyticsService
  ) {}

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
      // Set default fleet name to filename (without extension)
      this.fleetName.set(file.name.replace('.csv', ''));
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
      fleet_name: this.fleetName() || undefined  // Include fleet name if provided
    };

    console.log(`🚀 Sending batch request with ${batchRequest.vehicles.length} vehicles`);
    console.log(`Features in first vehicle: ${Object.keys(batchRequest.vehicles[0].features).length}`);
    console.log('Feature names:', Object.keys(batchRequest.vehicles[0].features).slice(0, 5));

    // Send batch prediction request
    this.apiService.predictBatch(batchRequest).subscribe({
      next: (response) => {
        console.log(`✅ Received ${response.total_count} predictions`);
        this.predictions.set(response.predictions);
        this.success.set(`Successfully processed ${response.total_count} vehicles`);
        this.processing.set(false);
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

    // Reset file input
    const fileInput = document.getElementById('csvFileInput') as HTMLInputElement;
    if (fileInput) {
      fileInput.value = '';
    }
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
