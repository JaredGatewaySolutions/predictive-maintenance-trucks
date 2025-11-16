import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { environment } from '../../../environments/environment';
import {
  Prediction,
  PredictionRequest,
  BatchPredictionRequest,
  BatchPredictionResponse,
  PredictionHistory
} from '../models/prediction.model';
import { HealthStatus, ApiMetrics } from '../models/health.model';
import { Explanation } from '../models/explanation.model';
import { Fleet, ReprocessFleetRequest } from '../models/fleet.model';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  /**
   * Health check endpoint
   */
  getHealth(): Observable<HealthStatus> {
    return this.http.get<HealthStatus>(`${this.apiUrl}/health`)
      .pipe(catchError(this.handleError));
  }

  /**
   * Get model metrics
   */
  getMetrics(): Observable<ApiMetrics> {
    return this.http.get<ApiMetrics>(`${this.apiUrl}/metrics`)
      .pipe(catchError(this.handleError));
  }

  /**
   * Single vehicle prediction
   */
  predictSingle(request: PredictionRequest): Observable<Prediction> {
    return this.http.post<Prediction>(`${this.apiUrl}/api/v1/predict`, request)
      .pipe(catchError(this.handleError));
  }

  /**
   * Batch predictions
   */
  predictBatch(request: BatchPredictionRequest): Observable<BatchPredictionResponse> {
    return this.http.post<BatchPredictionResponse>(`${this.apiUrl}/api/v1/predict/batch`, request)
      .pipe(catchError(this.handleError));
  }

  /**
   * Get prediction history for a vehicle
   */
  getPredictionHistory(vehicleId: string): Observable<PredictionHistory> {
    return this.http.get<PredictionHistory>(`${this.apiUrl}/api/v1/predictions/${vehicleId}`)
      .pipe(catchError(this.handleError));
  }

  /**
   * Get SHAP explanation for a vehicle
   */
  getExplanation(vehicleId: string): Observable<Explanation> {
    return this.http.get<Explanation>(`${this.apiUrl}/api/v1/explain/${vehicleId}`)
      .pipe(catchError(this.handleError));
  }

  /**
   * Get all available fleets
   */
  getFleets(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/api/v1/fleets`)
      .pipe(catchError(this.handleError));
  }

  /**
   * Get predictions for a specific fleet
   */
  getFleetPredictions(fleetId: string): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/api/v1/fleets/${fleetId}/predictions`)
      .pipe(catchError(this.handleError));
  }

  /**
   * Create a new fleet
   */
  createFleet(fleetName: string): Observable<Fleet> {
    return this.http.post<Fleet>(`${this.apiUrl}/api/v1/fleets`, null, {
      params: { fleet_name: fleetName }
    })
      .pipe(catchError(this.handleError));
  }

  /**
   * Delete a fleet
   */
  deleteFleet(fleetId: string): Observable<any> {
    return this.http.delete<any>(`${this.apiUrl}/api/v1/fleets/${fleetId}`)
      .pipe(catchError(this.handleError));
  }

  /**
   * Reprocess a fleet with new data
   */
  reprocessFleet(request: ReprocessFleetRequest): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/api/v1/fleets/${request.fleet_id}/reprocess`, request)
      .pipe(catchError(this.handleError));
  }

  /**
   * Error handling
   */
  private handleError(error: HttpErrorResponse) {
    let errorMessage = 'An error occurred';

    if (error.error instanceof ErrorEvent) {
      // Client-side error
      errorMessage = `Error: ${error.error.message}`;
    } else {
      // Server-side error
      errorMessage = `Error Code: ${error.status}\nMessage: ${error.message}`;
      if (error.error?.detail) {
        errorMessage += `\nDetail: ${error.error.detail}`;
      }
    }

    console.error(errorMessage);
    return throwError(() => new Error(errorMessage));
  }
}
