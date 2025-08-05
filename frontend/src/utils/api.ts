import { API_BASE_URL } from '../lib/constants';

export interface ApiError {
  status: number;
  message: string;
  detail?: string;
}

export class ApiException extends Error {
  constructor(public apiError: ApiError) {
    super(apiError.message);
    this.name = 'ApiException';
  }
}

export const apiRequest = async (endpoint: string, options: RequestInit = {}) => {
  const token = localStorage.getItem('token');
  
  console.time(`API:${endpoint}`);
  console.log(`API Request: ${endpoint}`, { 
    method: options.method || 'GET',
    baseUrl: API_BASE_URL 
  });
  
  const defaultHeaders: HeadersInit = {};
  
  if (!(options.body instanceof FormData)) {
    defaultHeaders['Content-Type'] = 'application/json';
  }
  
  if (token) {
    defaultHeaders['Authorization'] = `Bearer ${token}`;
  }
  
  const config: RequestInit = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  };
  
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
    console.timeEnd(`API:${endpoint}`);
    console.log(`API Response: ${endpoint}`, { 
      status: response.status, 
      ok: response.ok 
    });
    
    if (response.status === 401) {
      localStorage.removeItem('token');
      window.location.reload();
      return;
    }
    
    if (!response.ok) {
      let errorMessage = 'An error occurred';
      let errorDetail = '';
      
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorData.message || errorMessage;
        errorDetail = errorData.detail || '';
      } catch {
        errorMessage = response.statusText || errorMessage;
      }
      
      const apiError: ApiError = {
        status: response.status,
        message: errorMessage,
        detail: errorDetail
      };
      
      throw new ApiException(apiError);
    }
    
    return response;
  } catch (error) {
    console.timeEnd(`API:${endpoint}`);
    console.error(`API_FAIL:${endpoint}`, {
      error: error instanceof Error ? error.message : 'Unknown error',
      baseUrl: API_BASE_URL,
      endpoint
    });
    
    if (error instanceof ApiException) {
      throw error;
    }
    
    throw new ApiException({
      status: 0,
      message: 'Network error. Please check your connection and try again.',
      detail: error instanceof Error ? error.message : 'Unknown error'
    });
  }
};
