import { buildAPIUrl } from '../utils/urlUtils';
import { RouteStop } from '../types/api';

export interface OptimizeRouteRequest {
  orders: Array<{
    id: string;
    customer_id: string;
    quantity: number;
  }>;
  location_id: string;
  vehicle_count?: number;
}

export interface OptimizeRouteResponse {
  routes: Array<{
    route_id: string;
    driver_id: string;
    stops: RouteStop[];
    total_distance: number;
    estimated_time: number;
    optimization_method: string;
  }>;
  total_routes: number;
  message: string;
}

export interface RouteProgress {
  route_id: string;
  completed_stops: number;
  total_stops: number;
  progress_percentage: number;
  current_stop?: RouteStop;
  estimated_completion?: string;
}

export class RouteService {
  static async optimizeRoutes(request: OptimizeRouteRequest): Promise<OptimizeRouteResponse> {
    const response = await fetch(buildAPIUrl('/api/routes/optimize'), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify(request),
      credentials: 'include'
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  }

  static async getRouteProgress(routeId: string): Promise<RouteProgress> {
    const response = await fetch(buildAPIUrl(`/api/routes/${routeId}/progress`), {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      credentials: 'include'
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  }

  static async updateDriverLocation(driverId: string, locationData: {
    lat: number;
    lng: number;
    timestamp: string;
    route_id?: string;
    speed?: number;
    heading?: number;
    accuracy?: number;
  }): Promise<{ status: string; message: string }> {
    const response = await fetch(buildAPIUrl(`/api/drivers/${driverId}/location`), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify(locationData),
      credentials: 'include'
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  }

  static async getDriverLocation(driverId: string): Promise<{
    lat: number;
    lng: number;
    timestamp: string;
    route_id?: string;
    speed?: number;
    heading?: number;
    accuracy?: number;
  }> {
    const response = await fetch(buildAPIUrl(`/api/drivers/${driverId}/location`), {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      credentials: 'include'
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  }
}
