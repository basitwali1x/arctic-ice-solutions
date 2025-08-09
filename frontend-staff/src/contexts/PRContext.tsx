import React, { createContext, useContext, ReactNode } from 'react';
import { useParams, useLocation } from 'react-router-dom';

interface PRContextType {
  prNumber: string | null;
  isPRContext: boolean;
  getNavigationPath: (path: string) => string;
}

const PRContext = createContext<PRContextType | undefined>(undefined);

export const usePR = () => {
  const context = useContext(PRContext);
  if (context === undefined) {
    throw new Error('usePR must be used within a PRProvider');
  }
  return context;
};

interface PRProviderProps {
  children: ReactNode;
}

export const PRProvider: React.FC<PRProviderProps> = ({ children }) => {
  const params = useParams();
  const location = useLocation();
  
  const prNumber = params.prNumber || null;
  const isPRContext = location.pathname.startsWith('/pr/');
  
  const getNavigationPath = (path: string): string => {
    if (isPRContext && prNumber) {
      return `/pr/${prNumber}${path}`;
    }
    return path;
  };

  const value = {
    prNumber,
    isPRContext,
    getNavigationPath,
  };

  return <PRContext.Provider value={value}>{children}</PRContext.Provider>;
};
