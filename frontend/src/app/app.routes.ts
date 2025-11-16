import { Routes } from '@angular/router';
import { DashboardComponent } from './features/dashboard/dashboard.component';
import { VehicleDetailComponent } from './features/vehicle-detail/vehicle-detail.component';
import { BatchUploadComponent } from './features/batch-upload/batch-upload.component';

export const routes: Routes = [
  { path: '', redirectTo: '/dashboard', pathMatch: 'full' },
  { path: 'dashboard', component: DashboardComponent },
  { path: 'vehicle/:id', component: VehicleDetailComponent },
  { path: 'upload', component: BatchUploadComponent },
  { path: '**', redirectTo: '/dashboard' }
];
