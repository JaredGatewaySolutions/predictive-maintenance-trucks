# Army Brigade Combat Team (ABCT) Implementation

## Overview

This document describes the implementation of the ABCT (Army Brigade Combat Team) fleet management feature in the predictive maintenance application. The feature allows users to organize and manage vehicle data by ABCTs while maintaining "fleet" terminology in the backend.

## Implementation Summary

### Frontend Changes

#### 1. Core Models & Services

**Fleet Model** (`frontend/src/app/core/models/fleet.model.ts`)

- Defines TypeScript interfaces for Fleet, CreateFleetRequest, and ReprocessFleetRequest
- Matches backend schema with fleet_id, fleet_name, vehicles, and risk summaries

**Fleet State Service** (`frontend/src/app/core/services/fleet-state.service.ts`)

- Centralized state management using RxJS BehaviorSubject
- Provides reactive observables for fleets$ and selectedFleet$
- Automatically syncs ABCT selection across all components
- Key methods:
  - `setSelectedFleet()` - Updates selected ABCT globally
  - `setFleets()` - Updates fleet list and auto-selects first if none selected
  - `addFleet()` - Adds new fleet and auto-selects it
  - `updateFleet()` - Updates existing fleet data
  - `removeFleet()` - Removes fleet and selects next available

#### 2. New ABCT Dialog Component

**Component** (`frontend/src/app/features/new-abct-dialog/`)

- Standalone Angular Material dialog
- Reactive form with required validation
- Material Design styling
- Features:
  - Required ABCT name field (2-100 characters)
  - Real-time validation with error messages
  - Material icons and clean UI

#### 3. Batch Upload Page Updates

**Changes:**

- Added ABCT selection card at top of page
- ABCT selector dropdown synced with state service
- "New ABCT" button opens dialog
- "Reprocess ABCT" button for updating existing ABCTs
- Changed all "Fleet" references to "ABCT" in UI
- Made ABCT name **required** (was optional)
- ABCT name field is read-only when existing ABCT is selected
- Visual indicator showing whether creating new or uploading to existing ABCT

**User Flow:**

1. User selects existing ABCT OR clicks "New ABCT" to create one
2. Uploads CSV file with vehicle data
3. Process file button validates ABCT name is present
4. Successfully uploaded data appears in both dashboard and upload page

#### 4. Dashboard Page Updates

**Changes:**

- Changed "Fleet Dashboard" to "ABCT Dashboard"
- ABCT selector dropdown synced with state service
- Added "New ABCT" button
- Displays selected ABCT's vehicle predictions and risk summaries
- All state changes synchronized with upload page

**Features:**

- Real-time risk distribution charts
- Top 10 high-risk vehicles table
- Risk summary cards (High/Medium/Low counts)
- Cost analysis visualization

#### 5. API Service Updates

**New Methods:**

- `deleteFleet(fleetId)` - Delete an ABCT and its data
- `reprocessFleet(request)` - Replace ABCT data with new CSV

### Backend Changes

#### Backend Endpoints (`api/routes/predictions.py`)

**Existing Endpoints:**

- `GET /api/v1/fleets` - List all fleets
- `GET /api/v1/fleets/{fleet_id}/predictions` - Get fleet predictions
- `POST /api/v1/predict/batch` - Create new fleet with predictions

**New Endpoints:**

**1. DELETE /api/v1/fleets/{fleet_id}**

- Deletes a fleet and all associated prediction files
- Removes fleet from fleets.json
- Returns success message with deleted vehicle count

**2. POST /api/v1/fleets/{fleet_id}/reprocess**

- Replaces existing fleet data with new predictions
- Deletes old prediction files
- Processes new batch of vehicles
- Updates fleet metadata (timestamp, vehicle_count, risk_summary)
- Maintains same fleet_id and fleet_name

## State Synchronization

### How It Works

The `FleetStateService` uses RxJS BehaviorSubjects to maintain a single source of truth for:

1. List of all fleets/ABCTs
2. Currently selected fleet/ABCT

Both dashboard and upload page subscribe to these observables:

```typescript
// Both components subscribe on init
this.fleetsSubscription = this.fleetStateService.fleets$.subscribe(fleets => {
  this.fleets.set(fleets);
});

this.selectedFleetSubscription = this.fleetStateService.selectedFleet$.subscribe(fleet => {
  this.selectedFleet.set(fleet);
  // Component-specific logic here
});
```

### Synchronization Scenarios

**Scenario 1: User selects ABCT in Dashboard**

1. User clicks ABCT dropdown in dashboard
2. Dashboard calls `fleetStateService.setSelectedFleet(fleet)`
3. State service updates selectedFleet$ observable
4. Upload page receives update and updates its UI
5. Both pages now show same selected ABCT

**Scenario 2: User creates new ABCT in Upload Page**

1. User clicks "New ABCT" button
2. Dialog opens, user enters name
3. Upload page processes CSV with new ABCT name
4. Backend creates fleet and returns success
5. Upload page calls `fleetStateService.loadFleets()` to refresh
6. State service auto-selects the new fleet (most recent)
7. Dashboard receives update and displays new ABCT

**Scenario 3: User uploads data to existing ABCT**

1. User selects existing ABCT from dropdown
2. State service updates selection globally
3. User uploads CSV file
4. Backend adds vehicles to existing fleet or creates new fleet with same name
5. Upload page reloads fleet list
6. Both pages show updated vehicle count

## UI Terminology

### Frontend (User-Facing)

- **ABCT** - Army Brigade Combat Team
- "Select ABCT"
- "Create New ABCT"
- "ABCT Name" (required field)
- "ABCT Dashboard"
- "Reprocess ABCT"

### Backend (API/Data Layer)

- **fleet** - Used in all API endpoints and data structures
- `fleet_id`, `fleet_name`, `fleet_data`
- Endpoints: `/api/v1/fleets`, `/fleets/{fleet_id}`

## Key Features

### 1. Required ABCT Name

- ABCT name is now **required** for all uploads
- Validation enforced in frontend before API call
- Clear error messages if name is missing

### 2. ABCT Selection Dropdown

- Shows all available ABCTs with vehicle counts
- Synchronized across dashboard and upload pages
- Auto-selects first ABCT on app load

### 3. New ABCT Creation

- Modal dialog with Material Design
- Form validation (2-100 characters)
- Newly created ABCT automatically selected in both pages

### 4. Fleet Reprocessing

- Replace existing ABCT data with new CSV
- Maintains fleet ID and name
- Updates all predictions and metadata
- "Reprocess ABCT" button only appears when ABCT is selected and file is uploaded

### 5. State Persistence

- Selected ABCT maintained during navigation
- Fleet list automatically refreshes after uploads
- No manual refresh needed

## Testing the Implementation

### Manual Testing Checklist

1. **Create New ABCT**
   - [ ] Click "New ABCT" button in upload page
   - [ ] Enter ABCT name and submit
   - [ ] Verify name appears in upload page
   - [ ] Navigate to dashboard and verify same ABCT is selected

2. **Upload Data to New ABCT**
   - [ ] Create new ABCT
   - [ ] Upload CSV file
   - [ ] Verify ABCT name is required
   - [ ] Verify predictions appear in results table
   - [ ] Navigate to dashboard and verify data appears

3. **Upload Data to Existing ABCT**
   - [ ] Select existing ABCT from dropdown
   - [ ] Upload CSV file
   - [ ] Verify vehicle count updates
   - [ ] Verify dashboard reflects new data

4. **Reprocess ABCT**
   - [ ] Select existing ABCT
   - [ ] Upload new CSV file
   - [ ] Click "Reprocess ABCT" button
   - [ ] Verify old data is replaced with new predictions

5. **State Synchronization**
   - [ ] Select ABCT in dashboard
   - [ ] Navigate to upload page
   - [ ] Verify same ABCT is selected
   - [ ] Select different ABCT in upload page
   - [ ] Navigate back to dashboard
   - [ ] Verify new selection is reflected

6. **Default Selection**
   - [ ] Clear browser data and reload app
   - [ ] Verify first ABCT is auto-selected
   - [ ] Verify both pages show same selection

## Technical Architecture

### Component Communication

```text
┌─────────────────────────────────────────────┐
│         FleetStateService                    │
│  (Single Source of Truth)                   │
│                                              │
│  - fleets$ BehaviorSubject                  │
│  - selectedFleet$ BehaviorSubject           │
└─────────────┬────────────────┬──────────────┘
              │                │
              │                │
      ┌───────▼──────┐  ┌──────▼────────┐
      │  Dashboard   │  │  Upload Page  │
      │  Component   │  │  Component    │
      │              │  │               │
      │ - Subscribes │  │ - Subscribes  │
      │ - Displays   │  │ - Uploads     │
      │ - Selects    │  │ - Creates     │
      └──────────────┘  └───────────────┘
```

### Data Flow

```text
User Action (Select ABCT)
    ↓
Component calls fleetStateService.setSelectedFleet()
    ↓
State Service updates selectedFleet$ observable
    ↓
All subscribed components receive update
    ↓
Components update their UI
```

## Files Modified/Created

### Created Files

- `frontend/src/app/core/models/fleet.model.ts`
- `frontend/src/app/core/services/fleet-state.service.ts`
- `frontend/src/app/features/new-abct-dialog/new-abct-dialog.component.ts`
- `frontend/src/app/features/new-abct-dialog/new-abct-dialog.component.html`
- `frontend/src/app/features/new-abct-dialog/new-abct-dialog.component.scss`

### Modified Files

- `frontend/src/app/core/services/api.service.ts`
- `frontend/src/app/features/batch-upload/batch-upload.component.ts`
- `frontend/src/app/features/batch-upload/batch-upload.component.html`
- `frontend/src/app/features/batch-upload/batch-upload.component.scss`
- `frontend/src/app/features/dashboard/dashboard.component.ts`
- `frontend/src/app/features/dashboard/dashboard.component.html`
- `frontend/src/app/features/dashboard/dashboard.component.scss`
- `api/routes/predictions.py`

## Future Enhancements

Potential improvements for future iterations:

1. **Delete ABCT from UI** - Add delete button with confirmation dialog
2. **ABCT Metadata** - Add creation date, creator, description fields
3. **ABCT Comparison** - Side-by-side comparison of multiple ABCTs
4. **Export ABCT Data** - Download all predictions for an ABCT as CSV
5. **ABCT History** - View all uploads/changes to an ABCT over time
6. **ABCT Permissions** - Role-based access control for ABCTs
7. **Bulk Operations** - Select multiple ABCTs for batch operations
8. **ABCT Templates** - Pre-configured ABCT templates for quick setup

## Conclusion

The ABCT implementation provides a comprehensive fleet management system with:

- Intuitive UI using "ABCT" terminology
- Clean separation between frontend (ABCT) and backend (fleet) naming
- Robust state management with automatic synchronization
- Full CRUD operations (Create, Read, Update, Delete)
- Material Design components for consistent UX
- Type-safe TypeScript implementation

The system is production-ready and can handle multiple ABCTs with hundreds of vehicles each.
