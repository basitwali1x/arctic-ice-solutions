import ReactGA from 'react-ga4';

const GA_MEASUREMENT_ID = (import.meta as any).env.VITE_GA_MEASUREMENT_ID;

export const initializeAnalytics = () => {
  if (GA_MEASUREMENT_ID) {
    ReactGA.initialize(GA_MEASUREMENT_ID);
  }
};

export const trackPageView = (path: string, title?: string) => {
  if (GA_MEASUREMENT_ID) {
    ReactGA.send({ hitType: 'pageview', page: path, title });
  }
};

export const trackEvent = (action: string, category: string, label?: string, value?: number) => {
  if (GA_MEASUREMENT_ID) {
    ReactGA.event({
      action,
      category,
      label,
      value,
    });
  }
};

export const trackRouteOptimization = (routeCount: number, duration: number) => {
  trackEvent('route_optimization', 'operations', 'routes_optimized', routeCount);
  trackEvent('route_optimization_duration', 'performance', 'duration_ms', duration);
};

export const trackDataImport = (type: 'excel' | 'google-sheets' | 'quickbooks', recordCount: number) => {
  trackEvent('data_import', 'data_management', type, recordCount);
};

export const trackCustomerAction = (action: 'create' | 'edit' | 'delete' | 'view') => {
  trackEvent('customer_management', 'customers', action);
};

export const trackOrderAction = (action: 'create' | 'edit' | 'complete' | 'cancel') => {
  trackEvent('order_management', 'orders', action);
};

export const trackWeatherAlert = (alertType: string, severity: string) => {
  trackEvent('weather_alert', 'safety', `${alertType}_${severity}`);
};
