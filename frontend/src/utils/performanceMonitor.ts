import { getVitalsScore, getDeviceType } from './vitals-benchmarks';

interface PerformanceMetrics {
  lcp: number;
  fcp: number;
  cls: number;
  inp: number;
  ttfb: number;
}

export class PerformanceMonitor {
  private metrics: Partial<PerformanceMetrics> = {};
  private deviceType = getDeviceType();

  updateMetric(name: keyof PerformanceMetrics, value: number) {
    this.metrics[name] = value;
    
    const score = getVitalsScore(name.toUpperCase(), value, this.deviceType);
    
    if (typeof window !== 'undefined' && window.location.hostname === 'localhost') {
      console.log(`📊 ${name.toUpperCase()}: ${value}ms (${score})`, {
        value,
        score,
        deviceType: this.deviceType,
        threshold: this.getThreshold(name)
      });
    }

    if (score === 'poor') {
      this.reportPoorPerformance(name, value);
    }
  }

  private getThreshold(metric: keyof PerformanceMetrics) {
    const thresholds = {
      lcp: this.deviceType === 'DASHBOARDS' ? 1800 : 2000,
      fcp: 1000,
      cls: this.deviceType === 'DASHBOARDS' ? 0.08 : 0.1,
      inp: 200,
      ttfb: 600
    };
    return thresholds[metric];
  }

  private reportPoorPerformance(metric: string, value: number) {
    if (typeof window !== 'undefined' && (window as any).Sentry) {
      (window as any).Sentry.captureMessage(`Poor ${metric.toUpperCase()} performance: ${value}`, {
        level: 'warning',
        tags: {
          performance: true,
          metric,
          deviceType: this.deviceType
        }
      });
    }
  }

  getMetrics() {
    return { ...this.metrics };
  }

  getOverallScore() {
    const scores = Object.entries(this.metrics).map(([name, value]) => 
      getVitalsScore(name.toUpperCase(), value, this.deviceType)
    );

    const goodCount = scores.filter(s => s === 'good').length;
    const totalCount = scores.length;

    if (totalCount === 0) return 'unknown';
    if (goodCount === totalCount) return 'good';
    if (goodCount / totalCount >= 0.75) return 'needs-improvement';
    return 'poor';
  }
}

export const performanceMonitor = new PerformanceMonitor();

if (typeof window !== 'undefined' && window.location.hostname === 'localhost') {
  (window as any).performanceMonitor = performanceMonitor;
}
