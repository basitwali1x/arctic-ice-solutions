export const VITALS_STANDARDS = {
  MOBILE: {
    LCP: { good: 2500, poor: 4000 },
    INP: { good: 200, poor: 500 },
    CLS: { good: 0.1, poor: 0.25 }
  },
  DESKTOP: {
    LCP: { good: 2000, poor: 3500 },
    INP: { good: 200, poor: 500 }, 
    CLS: { good: 0.05, poor: 0.2 }
  },
  DASHBOARDS: {
    LCP: { good: 1800, poor: 3000 },
    INP: { good: 200, poor: 500 },
    CLS: { good: 0.08, poor: 0.15 }
  }
};

export const getVitalsScore = (metric: string, value: number, deviceType: keyof typeof VITALS_STANDARDS = 'DESKTOP') => {
  const thresholds = VITALS_STANDARDS[deviceType];
  const metricThresholds = thresholds[metric as keyof typeof thresholds];
  
  if (!metricThresholds) return 'unknown';
  
  if (value <= metricThresholds.good) return 'good';
  if (value >= metricThresholds.poor) return 'poor';
  return 'needs-improvement';
};

export const getDeviceType = (): keyof typeof VITALS_STANDARDS => {
  if (typeof window === 'undefined') return 'DESKTOP';
  
  const userAgent = navigator.userAgent;
  const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(userAgent);
  const isDashboard = window.location.pathname.includes('/dashboard');
  
  if (isDashboard) return 'DASHBOARDS';
  if (isMobile) return 'MOBILE';
  return 'DESKTOP';
};
