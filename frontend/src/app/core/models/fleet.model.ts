export interface Fleet {
  fleet_id: string;
  fleet_name: string;
  upload_timestamp: string;
  vehicle_count: number;
  vehicle_ids: string[];
  risk_summary: {
    high: number;
    medium: number;
    low: number;
  };
}

export interface CreateFleetRequest {
  fleet_name: string;
}

export interface ReprocessFleetRequest {
  fleet_id: string;
  csv_data: any[];
}
