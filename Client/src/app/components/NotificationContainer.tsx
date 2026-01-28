import { useEffect, useState } from 'react';
import { notificationService, NotificationData } from '../services/notificationService';
import { CheckCircle2, XCircle, Info, AlertTriangle, X } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';

/**
 * Global Notification Container
 * 
 * Renders notifications from the notification service.
 * This component should be placed once at the app root level.
 */
export function NotificationContainer() {
  const [notifications, setNotifications] = useState<NotificationData[]>([]);

  useEffect(() => {
    const unsubscribe = notificationService.subscribe((notification) => {
      if (notification.dismiss) {
        setNotifications(prev => prev.filter(n => n.id !== notification.id));
        return;
      }
      setNotifications(prev => [...prev, notification]);

      // Auto-dismiss after duration
      if (notification.duration && !notification.isLoading) {
        setTimeout(() => {
          setNotifications(prev => prev.filter(n => n.id !== notification.id));
        }, notification.duration);
      }
    });

    return unsubscribe;
  }, []);

  const removeNotification = (id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-2 max-w-md">
      <AnimatePresence>
        {notifications.map((notification) => (
          <motion.div
            key={notification.id}
            initial={{ opacity: 0, y: -20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, x: 100, scale: 0.95 }}
            className={`
              flex items-start gap-3 p-4 rounded-lg shadow-lg border
              ${getNotificationStyles(notification.type)}
            `}
          >
            <div className="flex-shrink-0">
              {getNotificationIcon(notification.type, notification.isLoading)}
            </div>
            
            <div className="flex-1 min-w-0">
              {notification.title && (
                <h4 className="font-semibold text-sm mb-1">{notification.title}</h4>
              )}
              <p className="text-sm">{notification.message}</p>
              {notification.description && (
                <p className="text-xs mt-1 opacity-80">{notification.description}</p>
              )}
              {notification.action && (
                <button
                  onClick={notification.action.onClick}
                  className="text-xs font-medium mt-2 underline hover:no-underline"
                >
                  {notification.action.label}
                </button>
              )}
            </div>

            {!notification.isLoading && (
              <button
                onClick={() => removeNotification(notification.id)}
                className="flex-shrink-0 opacity-60 hover:opacity-100 transition-opacity"
              >
                <X className="h-4 w-4" />
              </button>
            )}
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}

function getNotificationStyles(type: string): string {
  switch (type) {
    case 'success':
      return 'bg-green-50 border-green-200 text-green-900';
    case 'error':
      return 'bg-red-50 border-red-200 text-red-900';
    case 'warning':
      return 'bg-orange-50 border-orange-200 text-orange-900';
    case 'info':
    default:
      return 'bg-blue-50 border-blue-200 text-blue-900';
  }
}

function getNotificationIcon(type: string, isLoading?: boolean) {
  if (isLoading) {
    return (
      <div className="animate-spin rounded-full h-5 w-5 border-2 border-blue-600 border-t-transparent" />
    );
  }

  switch (type) {
    case 'success':
      return <CheckCircle2 className="h-5 w-5 text-green-600" />;
    case 'error':
      return <XCircle className="h-5 w-5 text-red-600" />;
    case 'warning':
      return <AlertTriangle className="h-5 w-5 text-orange-600" />;
    case 'info':
    default:
      return <Info className="h-5 w-5 text-blue-600" />;
  }
}
