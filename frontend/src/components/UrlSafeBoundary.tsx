import React from 'react';
import { buildAPIUrl } from '../utils/urlUtils';

interface UrlSafeBoundaryProps {
  children: React.ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
}

class ErrorBoundary extends React.Component<{children: React.ReactNode, fallback: (error: Error) => React.ReactNode}, ErrorBoundaryState> {
  constructor(props: any) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('URL Configuration Error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError && this.state.error) {
      return this.props.fallback(this.state.error);
    }

    return this.props.children;
  }
}

const UrlSafeBoundary = ({ children }: UrlSafeBoundaryProps) => {
  const validateUrls = () => {
    try {
      buildAPIUrl('/health-check');
      return true;
    } catch (error) {
      console.error('URL Configuration Error:', error);
      return false;
    }
  };

  return (
    <ErrorBoundary
      fallback={(error) => (
        <div className="url-error p-4 bg-red-50 border border-red-200 rounded-lg">
          <h2 className="text-lg font-semibold text-red-800 mb-2">URL Configuration Error</h2>
          <pre className="text-sm text-red-600 mb-4">{error.message}</pre>
          <button 
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Retry
          </button>
        </div>
      )}
    >
      {validateUrls() ? children : (
        <div className="p-4 text-center">Validating URL configuration...</div>
      )}
    </ErrorBoundary>
  );
};

export default UrlSafeBoundary;
