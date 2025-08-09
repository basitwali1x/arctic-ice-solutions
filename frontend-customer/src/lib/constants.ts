import { buildAPIUrl } from '../utils/urlUtils';

export const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://app-rawyclbe.fly.dev';

export const RouteService = {
  async optimizeRoute(locationId: string): Promise<any> {
    const response = await fetch(buildAPIUrl(`/api/routes/optimize?location_id=${locationId}`), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      credentials: 'include'
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  },

  async getRouteProgress(routeId: string): Promise<any> {
    const response = await fetch(buildAPIUrl(`/api/routes/${routeId}/progress`), {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      credentials: 'include'
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  },

  async updateDriverLocation(driverId: string, locationData: any): Promise<any> {
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
};
