/**
 * Notification Service Abstraction Layer
 * 
 * This service provides a unified interface for showing notifications.
 * The underlying library can be swapped without changing consumer code.
 * 
 * Current implementation: Browser-native notifications with fallback
 * Can be replaced with: react-hot-toast, sonner, react-toastify, etc.
 */

type NotificationType = 'success' | 'error' | 'info' | 'warning';
interface NotificationOptions {
  title?: string;
  description?: string;
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
}

class NotificationService {
  private listeners: Array<(notification: NotificationData) => void> = [];

  /**
   * Show a success notification
   */
  success(message: string, options?: NotificationOptions): void {
    this.show('success', message, options);
  }

  /**
   * Show an error notification
   */
  error(message: string, options?: NotificationOptions): void {
    this.show('error', message, options);
  }

  /**
   * Show an info notification
   */
  info(message: string, options?: NotificationOptions): void {
    this.show('info', message, options);
  }

  /**
   * Show a warning notification
   */
  warning(message: string, options?: NotificationOptions): void {
    this.show('warning', message, options);
  }

  /**
   * Show a loading notification
   * Returns a function to dismiss it
   */
  loading(message: string): () => void {
    const id = Math.random().toString(36);
    this.notify({
      id,
      type: 'info',
      message,
      isLoading: true,
    });
    
    return () => this.dismiss(id);
  }

  /**
   * Subscribe to notification events
   */
  subscribe(callback: (notification: NotificationData) => void): () => void {
    this.listeners.push(callback);
    return () => {
      this.listeners = this.listeners.filter(l => l !== callback);
    };
  }

  /**
   * Internal method to show notification
   */
  private show(type: NotificationType, message: string, options?: NotificationOptions): void {
    const notification: NotificationData = {
      id: Math.random().toString(36),
      type,
      message,
      title: options?.title,
      description: options?.description,
      duration: options?.duration ?? this.getDefaultDuration(type),
      action: options?.action,
    };

    this.notify(notification);
  }

  /**
   * Notify all listeners
   */
  private notify(notification: NotificationData): void {
    this.listeners.forEach(listener => listener(notification));
  }

  /**
   * Dismiss a notification by ID
   */
  private dismiss(id: string): void {
    this.listeners.forEach(listener => 
      listener({ id, type: 'info', message: '', dismiss: true })
    );
  }

  /**
   * Get default duration based on type
   */
  private getDefaultDuration(type: NotificationType): number {
    switch (type) {
      case 'error':
        return 5000;
      case 'success':
        return 3000;
      case 'warning':
        return 4000;
      case 'info':
      default:
        return 3000;
    }
  }
}

export interface NotificationData {
  id: string;
  type: NotificationType;
  message: string;
  title?: string;
  description?: string;
  duration?: number;
  isLoading?: boolean;
  dismiss?: boolean;
  action?: {
    label: string;
    onClick: () => void;
  };
}

// Singleton instance
export const notificationService = new NotificationService();
