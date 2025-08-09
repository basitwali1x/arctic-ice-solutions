import { useToast } from './use-toast';
import { ApiException } from '../utils/api';

export const useErrorToast = () => {
  const { toast } = useToast();

  const showError = (error: unknown, fallbackMessage = 'An unexpected error occurred') => {
    let title = 'Error';
    let description = fallbackMessage;

    if (error instanceof ApiException) {
      switch (error.apiError.status) {
        case 403:
          title = 'Access Denied';
          description = 'You do not have permission to access this resource.';
          break;
        case 404:
          title = 'Not Found';
          description = 'The requested resource was not found.';
          break;
        case 500:
          title = 'Server Error';
          description = 'A server error occurred. Please try again later.';
          break;
        case 400:
          title = 'Invalid Data';
          description = error.apiError.message || 'The data provided is invalid or malformed.';
          break;
        default:
          description = error.apiError.message;
      }
    } else if (error instanceof Error) {
      description = error.message;
    }

    toast({
      variant: 'destructive',
      title,
      description,
    });
  };

  return { showError };
};
