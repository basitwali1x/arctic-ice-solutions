import React, { Profiler, useState, useEffect } from 'react';

interface ProfilerData {
  id: string;
  phase: 'mount' | 'update' | 'nested-update';
  actualDuration: number;
  baseDuration: number;
  startTime: number;
  commitTime: number;
}

export const PerformanceProfiler: React.FC<{ children: React.ReactNode; id: string }> = ({ children, id }) => {
  const [, setProfileData] = useState<ProfilerData[]>([]);

  const onRender: React.ProfilerOnRenderCallback = (
    id,
    phase,
    actualDuration,
    baseDuration,
    startTime,
    commitTime
  ) => {
    const data: ProfilerData = {
      id,
      phase,
      actualDuration,
      baseDuration,
      startTime,
      commitTime
    };

    setProfileData(prev => [...prev.slice(-9), data]);

    if (typeof window !== 'undefined' && window.location.hostname === 'localhost') {
      if (actualDuration > 16) {
        console.warn(`🐌 Slow render detected in ${id}:`, {
          phase,
          actualDuration: `${actualDuration.toFixed(2)}ms`,
          baseDuration: `${baseDuration.toFixed(2)}ms`,
          efficiency: `${((baseDuration / actualDuration) * 100).toFixed(1)}%`
        });
      }

      performance.mark(`${id}-${phase}-end`);
      console.table({
        Component: id,
        Phase: phase,
        Duration: `${actualDuration.toFixed(2)}ms`,
        BaseDuration: `${baseDuration.toFixed(2)}ms`,
        Efficiency: `${((baseDuration / actualDuration) * 100).toFixed(1)}%`
      });
    }
  };

  return (
    <Profiler id={id} onRender={onRender}>
      {children}
    </Profiler>
  );
};

export const useProfilerData = () => {
  const [data] = useState<ProfilerData[]>([]);
  
  useEffect(() => {
    if (typeof window !== 'undefined' && window.location.hostname === 'localhost') {
      (window as any).getProfilerData = () => data;
    }
  }, [data]);

  return data;
};

export const DashboardProfiler: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <PerformanceProfiler id="Dashboard">
    {children}
  </PerformanceProfiler>
);
