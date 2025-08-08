class SafeURL {
  private readonly url: URL;
  
  constructor(base: string, path: string) {
    this.url = new URL(path, base);
    
    if (!this.url.protocol.startsWith('https') && !this.url.hostname.includes('localhost')) {
      throw new Error(`Insecure URL: ${this.url.toString()}`);
    }
  }
  
  toString(): string {
    return this.url.toString();
  }
}

export const buildAPIUrl = (path: string): string => {
  const baseUrl = (import.meta as any).env?.VITE_API_URL || 'https://app-rawyclbe.fly.dev';
  return new SafeURL(baseUrl, path).toString();
};

export const validateURL = (url: string): boolean => {
  try {
    const parsedUrl = new URL(url);
    return parsedUrl.protocol === 'https:' || parsedUrl.hostname.includes('localhost');
  } catch {
    return false;
  }
};

export const getDriverRouteUrl = (driverId: string): string => 
  buildAPIUrl(`/api/drivers/${encodeURIComponent(driverId)}/location`);

export const getRouteProgressUrl = (routeId: string): string =>
  buildAPIUrl(`/api/routes/${encodeURIComponent(routeId)}/progress`);

export const getSubdomain = (): string | null => {
  if (typeof window === 'undefined') return null;
  
  const hostname = window.location.hostname;
  const parts = hostname.split('.');
  
  if (parts.length >= 3 && !hostname.includes('localhost')) {
    return parts[0];
  }
  
  return null;
};
