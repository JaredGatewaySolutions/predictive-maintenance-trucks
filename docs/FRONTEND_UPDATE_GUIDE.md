# Frontend Update Guide
## Updating Forms for Optimal 20 Features

**Date:** November 15, 2025  
**Purpose:** Update Angular frontend to collect optimal 20 features instead of 105

---

## Overview

The frontend needs to be updated to collect only the **20 scientifically-selected optimal features** instead of the previous 105 features. This will:
- ✅ Reduce user input time by 80% (15 min → 3 min)
- ✅ Improve user experience dramatically
- ✅ Reduce input errors (fewer fields = fewer mistakes)
- ✅ Match the new model v5_20251115_223658 requirements

---

## The 20 Required Features

### Feature Groups

| Group | Features | Priority |
|-------|----------|----------|
| **System Diagnostics** | 158_9, 158_5, 158_6 | 🔴 Highest |
| **Temperature/Environment** | 167_6, 167_3, 167_1 | 🟠 High |
| **Operational Stress** | 459_3, 459_15, 459_8, 459_14, 459_9, 459_1 | 🟡 Medium-High |
| **Load Distribution** | 272_0, 272_2, 272_4 | 🟢 Medium |
| **Terrain/Mobility** | 291_4, 291_1, 291_5 | 🔵 Medium |
| **Component Wear** | 397_33, 397_0, 397_3 | 🟣 Medium |

---

## Recommended Form Layout

### Option A: Single Page Form (Recommended)

```
┌─────────────────────────────────────────────────────────┐
│  Predictive Maintenance - Vehicle Assessment            │
│                                                          │
│  Vehicle ID: [__________]                               │
│                                                          │
│  ┌─ System Diagnostics (Highest Priority) ──────────┐   │
│  │ Power System Metric 9:  [________] 🔴 CRITICAL  │   │
│  │ Power System Metric 5:  [________]               │   │
│  │ Power System Metric 6:  [________]               │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  ┌─ Temperature & Environment ──────────────────────┐   │
│  │ Moderate Temp Operations: [________]             │   │
│  │ Cold Weather Operations:  [________]             │   │
│  │ Low Temperature Ops:      [________]             │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  ┌─ Operational Stress ──────────────────────────────┐  │
│  │ Stress Level 3:  [________]                       │  │
│  │ Stress Level 15: [________]                       │  │
│  │ Stress Level 8:  [________]                       │  │
│  │ Stress Level 14: [________]                       │  │
│  │ Stress Level 9:  [________]                       │  │
│  │ Stress Level 1:  [________]                       │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  [Show More Groups...]                                   │
│                                                          │
│  [Submit Assessment]  [Clear Form]                       │
└─────────────────────────────────────────────────────────┘
```

### Option B: Multi-Step Wizard (For Complex Scenarios)

```
Step 1: System Diagnostics (3 fields)
Step 2: Environment & Stress (9 fields)
Step 3: Load & Terrain (6 fields)
Step 4: Component Wear (3 fields)
Step 5: Review & Submit
```

---

## Implementation Steps

### 1. Update TypeScript Models

**File:** `frontend/src/app/core/models/prediction.model.ts`

```typescript
// Update the VehicleFeatures interface
export interface VehicleFeatures {
  // System Diagnostics & Performance
  '158_9': number;   // Power System Metric 9 (MOST IMPORTANT)
  '158_5': number;   // Power System Metric 5
  '158_6': number;   // Power System Metric 6
  
  // Temperature & Environmental
  '167_6': number;   // Moderate Temperature Operations
  '167_3': number;   // Cold Weather Operations
  '167_1': number;   // Low Temperature Operations
  
  // Terrain & Mobility
  '291_4': number;   // Terrain Type 4
  '291_1': number;   // Terrain Type 1
  '291_5': number;   // Terrain Type 5
  
  // Operational Stress
  '459_3': number;   // Operational Stress 3
  '459_15': number;  // Operational Stress 15
  '459_8': number;   // Operational Stress 8
  '459_14': number;  // Operational Stress 14
  '459_9': number;   // Operational Stress 9
  '459_1': number;   // Operational Stress 1
  
  // Load Distribution
  '272_0': number;   // Load Distribution 0
  '272_2': number;   // Load Distribution 2
  '272_4': number;   // Load Distribution 4
  
  // Component Wear
  '397_33': number;  // Component Wear 33
  '397_0': number;   // Component Wear 0
  '397_3': number;   // Component Wear 3
}

// Helper: Feature metadata for form generation
export interface FeatureMetadata {
  code: string;
  displayName: string;
  description: string;
  group: string;
  importance: number;
  priority: 'highest' | 'high' | 'medium' | 'low';
  placeholder?: string;
  min?: number;
  max?: number;
}

export const OPTIMAL_FEATURES: FeatureMetadata[] = [
  {
    code: '158_9',
    displayName: 'Power System Metric 9',
    description: 'Most important predictor - Power system performance indicator',
    group: 'System Diagnostics',
    importance: 3.41,
    priority: 'highest',
    placeholder: 'e.g., 1250.5'
  },
  // ... add all 20 features
];
```

### 2. Update Component Template

**File:** `frontend/src/app/features/vehicle-detail/vehicle-detail.component.html`

Replace the existing large form with:

```html
<div class="vehicle-assessment-form">
  <h2>Vehicle Predictive Maintenance Assessment</h2>
  <p class="subtitle">Enter 20 key metrics (reduced from 105 for faster input)</p>
  
  <form [formGroup]="assessmentForm" (ngSubmit)="onSubmit()">
    
    <!-- Vehicle ID -->
    <mat-form-field class="full-width">
      <mat-label>Vehicle/Tank ID</mat-label>
      <input matInput formControlName="vehicleId" placeholder="TANK001" required>
    </mat-form-field>
    
    <!-- System Diagnostics (Highest Priority) -->
    <mat-expansion-panel expanded="true" class="priority-highest">
      <mat-expansion-panel-header>
        <mat-panel-title>
          <mat-icon>priority_high</mat-icon>
          System Diagnostics & Performance
        </mat-panel-title>
        <mat-panel-description>
          Highest Priority (3 fields) - Most Important!
        </mat-panel-description>
      </mat-expansion-panel-header>
      
      <div class="feature-group">
        <mat-form-field>
          <mat-label>Power System Metric 9 🔴</mat-label>
          <input matInput type="number" formControlName="field_158_9" 
                 placeholder="1250.5" required>
          <mat-hint>MOST IMPORTANT FEATURE (3.41% importance)</mat-hint>
        </mat-form-field>
        
        <mat-form-field>
          <mat-label>Power System Metric 5</mat-label>
          <input matInput type="number" formControlName="field_158_5" 
                 placeholder="980.3" required>
        </mat-form-field>
        
        <mat-form-field>
          <mat-label>Power System Metric 6</mat-label>
          <input matInput type="number" formControlName="field_158_6" 
                 placeholder="710.8" required>
        </mat-form-field>
      </div>
    </mat-expansion-panel>
    
    <!-- Temperature & Environmental -->
    <mat-expansion-panel>
      <mat-expansion-panel-header>
        <mat-panel-title>
          <mat-icon>thermostat</mat-icon>
          Temperature & Environmental Operations
        </mat-panel-title>
        <mat-panel-description>
          3 fields - Environmental conditions
        </mat-panel-description>
      </mat-expansion-panel-header>
      
      <div class="feature-group">
        <!-- Add 167_6, 167_3, 167_1 -->
      </div>
    </mat-expansion-panel>
    
    <!-- Operational Stress -->
    <mat-expansion-panel>
      <mat-expansion-panel-header>
        <mat-panel-title>
          <mat-icon>warning</mat-icon>
          Operational Stress & Usage
        </mat-panel-title>
        <mat-panel-description>
          6 fields - Stress patterns
        </mat-panel-description>
      </mat-expansion-panel-header>
      
      <div class="feature-group">
        <!-- Add 459_3, 459_15, 459_8, 459_14, 459_9, 459_1 -->
      </div>
    </mat-expansion-panel>
    
    <!-- Load Distribution -->
    <mat-expansion-panel>
      <mat-expansion-panel-header>
        <mat-panel-title>
          <mat-icon>fitness_center</mat-icon>
          Load & Weight Distribution
        </mat-panel-title>
        <mat-panel-description>
          3 fields - Load patterns
        </mat-panel-description>
      </mat-expansion-panel-header>
      
      <div class="feature-group">
        <!-- Add 272_0, 272_2, 272_4 -->
      </div>
    </mat-expansion-panel>
    
    <!-- Terrain & Mobility -->
    <mat-expansion-panel>
      <mat-expansion-panel-header>
        <mat-panel-title>
          <mat-icon>terrain</mat-icon>
          Terrain & Mobility
        </mat-panel-title>
        <mat-panel-description>
          3 fields - Terrain types
        </mat-panel-description>
      </mat-expansion-panel-header>
      
      <div class="feature-group">
        <!-- Add 291_4, 291_1, 291_5 -->
      </div>
    </mat-expansion-panel>
    
    <!-- Component Wear -->
    <mat-expansion-panel>
      <mat-expansion-panel-header>
        <mat-panel-title>
          <mat-icon>engineering</mat-icon>
          Component Wear & Degradation
        </mat-panel-title>
        <mat-panel-description>
          3 fields - Wear indicators
        </mat-panel-description>
      </mat-expansion-panel-header>
      
      <div class="feature-group">
        <!-- Add 397_33, 397_0, 397_3 -->
      </div>
    </mat-expansion-panel>
    
    <!-- Form Actions -->
    <div class="form-actions">
      <button mat-raised-button type="button" (click)="clearForm()">
        Clear Form
      </button>
      <button mat-raised-button color="primary" type="submit" 
              [disabled]="!assessmentForm.valid">
        Submit Assessment
      </button>
    </div>
  </form>
  
  <!-- Progress Indicator -->
  <div class="form-progress">
    <span>Progress: {{ getFormCompleteness() }}% complete</span>
    <mat-progress-bar mode="determinate" [value]="getFormCompleteness()">
    </mat-progress-bar>
  </div>
</div>
```

### 3. Update Component TypeScript

**File:** `frontend/src/app/features/vehicle-detail/vehicle-detail.component.ts`

```typescript
import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ApiService } from '../../core/services/api.service';

@Component({
  selector: 'app-vehicle-detail',
  templateUrl: './vehicle-detail.component.html',
  styleUrls: ['./vehicle-detail.component.scss']
})
export class VehicleDetailComponent implements OnInit {
  assessmentForm: FormGroup;
  
  // Feature groups for organization
  featureGroups = {
    systemDiagnostics: ['158_9', '158_5', '158_6'],
    temperature: ['167_6', '167_3', '167_1'],
    terrain: ['291_4', '291_1', '291_5'],
    operationalStress: ['459_3', '459_15', '459_8', '459_14', '459_9', '459_1'],
    loadDistribution: ['272_0', '272_2', '272_4'],
    componentWear: ['397_33', '397_0', '397_3']
  };
  
  constructor(
    private fb: FormBuilder,
    private apiService: ApiService
  ) {
    this.assessmentForm = this.createForm();
  }
  
  ngOnInit(): void {}
  
  private createForm(): FormGroup {
    const formConfig: any = {
      vehicleId: ['', Validators.required]
    };
    
    // Add all 20 feature fields
    Object.values(this.featureGroups).flat().forEach(code => {
      formConfig[`field_${code}`] = ['', [Validators.required, Validators.min(0)]];
    });
    
    return this.fb.group(formConfig);
  }
  
  getFormCompleteness(): number {
    const totalFields = 21; // 20 features + vehicle ID
    const filledFields = Object.keys(this.assessmentForm.value)
      .filter(key => this.assessmentForm.value[key] !== '' && this.assessmentForm.value[key] !== null)
      .length;
    return Math.round((filledFields / totalFields) * 100);
  }
  
  clearForm(): void {
    this.assessmentForm.reset();
  }
  
  onSubmit(): void {
    if (this.assessmentForm.valid) {
      const formData = this.assessmentForm.value;
      
      // Transform field_158_9 to 158_9 format for API
      const features: any = {};
      Object.keys(formData).forEach(key => {
        if (key.startsWith('field_')) {
          const featureCode = key.replace('field_', '');
          features[featureCode] = formData[key];
        }
      });
      
      const request = {
        vehicle_id: formData.vehicleId,
        features: features
      };
      
      this.apiService.predict(request).subscribe(
        response => {
          console.log('Prediction successful:', response);
          // Handle success (show result, navigate, etc.)
        },
        error => {
          console.error('Prediction failed:', error);
          // Handle error
        }
      );
    }
  }
}
```

### 4. Update Styling

**File:** `frontend/src/app/features/vehicle-detail/vehicle-detail.component.scss`

```scss
.vehicle-assessment-form {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
  
  .subtitle {
    color: #666;
    margin-bottom: 2rem;
  }
  
  .full-width {
    width: 100%;
    margin-bottom: 1rem;
  }
  
  mat-expansion-panel {
    margin-bottom: 1rem;
    
    &.priority-highest {
      border-left: 4px solid #f44336;
      
      mat-panel-title mat-icon {
        color: #f44336;
      }
    }
  }
  
  .feature-group {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1rem;
    padding: 1rem 0;
    
    mat-form-field {
      width: 100%;
    }
  }
  
  .form-actions {
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
    margin-top: 2rem;
  }
  
  .form-progress {
    margin-top: 1rem;
    
    span {
      display: block;
      margin-bottom: 0.5rem;
      font-size: 0.9rem;
      color: #666;
    }
  }
}
```

---

## Testing Checklist

- [ ] Form displays all 20 fields correctly
- [ ] Field validation works (required, numeric)
- [ ] Form submission sends correct data format
- [ ] API accepts the 20-feature payload
- [ ] Progress indicator updates correctly
- [ ] Clear button resets all fields
- [ ] Expansion panels work properly
- [ ] Mobile responsive design
- [ ] Accessibility (keyboard navigation, screen readers)
- [ ] Error handling and user feedback

---

## Migration Notes

### For Users

**Before (Old Form):**
- 105 fields to fill out
- ~15 minutes to complete
- High error rate
- Overwhelming experience

**After (New Form):**
- 20 fields to fill out (81% reduction!)
- ~3 minutes to complete
- Lower error rate
- Organized, manageable experience

### Feature Mapping Reference

Users with existing data in old format will need conversion. The system should:
1. Accept old 105-feature format temporarily
2. Extract the 20 optimal features
3. Log a deprecation warning
4. Return prediction as normal

---

## Quick Start Command

Once frontend changes are complete:

```bash
cd frontend
npm install  # If new dependencies added
ng serve     # Start development server
```

Then test at: `http://localhost:4200`

---

**Status:** 📝 **Ready for Implementation**  
**Estimated Development Time:** 4-6 hours  
**Priority:** 🔴 **HIGH** - Required for model v5 deployment  
**Dependencies:** API schemas already updated ✅
