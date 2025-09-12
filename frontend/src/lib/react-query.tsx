import { ReactNode, useMemo } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { ApiException } from '../utils/api';

const shouldRetry = (err: unknown) => {
  return err instanceof ApiException
    ? err.apiError.status === 0 || err.apiError.status >= 500
    : true;
};

export const makeQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        retry: (_failureCount, error) => shouldRetry(error),
        retryDelay: attemptIndex => Math.min(1000 * 2 ** attemptIndex, 30000),
        refetchOnWindowFocus: false,
        staleTime: 30_000,
      },
      mutations: {
        retry: (_failureCount, error) => shouldRetry(error),
        retryDelay: attemptIndex => Math.min(1000 * 2 ** attemptIndex, 30000),
      },
    },
  });

export function ReactQueryProvider({ children }: { children: ReactNode }) {
  const client = useMemo(() => makeQueryClient(), []);
  return (
    <QueryClientProvider client={client}>
      {children}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}
