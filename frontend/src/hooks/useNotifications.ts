import { useState, useEffect } from 'react';
import { Notification } from '../types/api';
import { apiRequest } from '../utils/api';

export function useNotifications() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchNotifications = async () => {
      try {
        setLoading(true);
        const response = await apiRequest('/api/notifications');
        if (response && response.ok) {
          const data = await response.json();
          setNotifications(Array.isArray(data) ? data : []);
          setError(null);
        } else {
          setNotifications([]);
          setError('Failed to fetch notifications');
        }
      } catch (error) {
        console.error('Failed to fetch notifications:', error);
        setNotifications([]);
        setError('Failed to fetch notifications');
      } finally {
        setLoading(false);
      }
    };

    fetchNotifications();
    const interval = setInterval(fetchNotifications, 30000);
    return () => clearInterval(interval);
  }, []);

  const unreadCount = notifications.filter(n => !n.read).length;

  return { notifications, unreadCount, loading, error };
}
