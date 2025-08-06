import { onCLS, onFCP, onINP, onLCP, onTTFB } from 'web-vitals';
import { performanceMonitor } from './performanceMonitor';
import { getVitalsScore, getDeviceType } from './vitals-benchmarks';

interface VitalsMetric {
  name: string;
  value: number;
  id: string;
  delta: number;
}

const sendToAnalytics = (metric: VitalsMetric) => {
  performanceMonitor.updateMetric(metric.name.toLowerCase() as any, metric.value);
  
  const deviceType = getDeviceType();
  const score = getVitalsScore(metric.name, metric.value, deviceType);

  const body = {
    event: 'web-vitals',
    event_data: {
      name: metric.name,
      value: metric.value,
      delta: metric.delta,
      id: metric.id,
      score,
      deviceType,
      path: window.location.pathname,
      userAgent: navigator.userAgent,
      timestamp: Date.now(),
    },
  };

  if (navigator.sendBeacon) {
    navigator.sendBeacon(
      '/api/analytics/vitals',
      new Blob([JSON.stringify(body)], { type: 'application/json' })
    );
  } else {
    fetch('/api/analytics/vitals', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    }).catch(console.error);
  }

  if (typeof window !== 'undefined' && window.location.hostname === 'localhost') {
    console.log(`📊 Web Vital - ${metric.name}: ${metric.value}ms (${score})`, {
      deviceType,
      threshold: deviceType === 'DASHBOARDS' ? 'strict' : 'standard'
    });
  }
};

export const reportWebVitals = () => {
  onCLS(sendToAnalytics, { reportAllChanges: true });
  onINP(sendToAnalytics);
  onLCP(sendToAnalytics);
  onFCP(sendToAnalytics);
  onTTFB(sendToAnalytics);
};

export const trackPageLoad = () => {
  if (typeof window !== 'undefined') {
    window.addEventListener('load', () => {
      setTimeout(reportWebVitals, 0);
    });
  }
};
