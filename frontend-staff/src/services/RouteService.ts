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

  static async completeDelivery(deliveryData: {
    stop_id: string;
    route_id: string;
    customer_id: string;
    bags_delivered: number;
    payment_method: string;
    payment_amount: number;
    notes?: string;
    signature_data?: string;
  }): Promise<{
    success: boolean;
    message: string;
    delivery_status: string;
    invoice_result: any;
    email_result: any;
    route_progress: any;
  }> {
    const response = await fetch(buildAPIUrl('/api/deliveries/complete'), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify(deliveryData)
    });

    if (!response.ok) {
      throw new Error(`Failed to complete delivery: ${response.statusText}`);
    }

    return await response.json();
  }

  static async generateAndSendInvoice(invoiceData: {
    customer_id: string;
    delivery_data: any;
    signature_data?: string;
  }): Promise<{
    success: boolean;
    message: string;
    invoice_result: any;
    email_result: any;
  }> {
    const response = await fetch(buildAPIUrl('/api/invoices/generate-and-send'), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify(invoiceData)
    });

    if (!response.ok) {
      throw new Error(`Failed to generate and send invoice: ${response.statusText}`);
    }

    return await response.json();
  }
}
