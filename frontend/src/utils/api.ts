const API_BASE_URL = import.meta.env?.VITE_API_URL || '';

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
