import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { Fleet } from '../models/fleet.model';

@Injectable({
  providedIn: 'root'
})
export class FleetStateService {
  private selectedFleetSubject = new BehaviorSubject<Fleet | null>(null);
  private fleetsSubject = new BehaviorSubject<Fleet[]>([]);

  selectedFleet$: Observable<Fleet | null> = this.selectedFleetSubject.asObservable();
  fleets$: Observable<Fleet[]> = this.fleetsSubject.asObservable();

  constructor() {}

  /**
   * Get the currently selected fleet
   */
  getSelectedFleet(): Fleet | null {
    return this.selectedFleetSubject.value;
  }

  /**
   * Set the selected fleet (syncs across all components)
   */
  setSelectedFleet(fleet: Fleet | null): void {
    this.selectedFleetSubject.next(fleet);
  }

  /**
   * Get all fleets
   */
  getFleets(): Fleet[] {
    return this.fleetsSubject.value;
  }

  /**
   * Update the fleets list
   */
  setFleets(fleets: Fleet[]): void {
    this.fleetsSubject.next(fleets);

    // Auto-select first fleet if none selected
    if (fleets.length > 0 && !this.selectedFleetSubject.value) {
      this.setSelectedFleet(fleets[0]);
    }
  }

  /**
   * Add a new fleet and auto-select it
   */
  addFleet(fleet: Fleet): void {
    const currentFleets = this.fleetsSubject.value;
    const updatedFleets = [fleet, ...currentFleets]; // Add to beginning
    this.setFleets(updatedFleets);
    this.setSelectedFleet(fleet);
  }

  /**
   * Update an existing fleet
   */
  updateFleet(fleet: Fleet): void {
    const currentFleets = this.fleetsSubject.value;
    const index = currentFleets.findIndex(f => f.fleet_id === fleet.fleet_id);

    if (index !== -1) {
      currentFleets[index] = fleet;
      this.setFleets([...currentFleets]);

      // If this was the selected fleet, update it
      if (this.selectedFleetSubject.value?.fleet_id === fleet.fleet_id) {
        this.setSelectedFleet(fleet);
      }
    }
  }

  /**
   * Remove a fleet
   */
  removeFleet(fleetId: string): void {
    const currentFleets = this.fleetsSubject.value;
    const updatedFleets = currentFleets.filter(f => f.fleet_id !== fleetId);
    this.setFleets(updatedFleets);

    // If the removed fleet was selected, select the first available fleet
    if (this.selectedFleetSubject.value?.fleet_id === fleetId) {
      this.setSelectedFleet(updatedFleets.length > 0 ? updatedFleets[0] : null);
    }
  }

  /**
   * Clear all state
   */
  clear(): void {
    this.selectedFleetSubject.next(null);
    this.fleetsSubject.next([]);
  }
}
