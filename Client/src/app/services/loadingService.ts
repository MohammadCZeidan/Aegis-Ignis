/**
 * Loading Service Abstraction Layer
 * 
 * This service manages global loading states.
 * Can be used for API calls, async operations, etc.
 * 
 * The underlying implementation can be swapped without changing consumer code.
 */

type LoadingListener = (isLoading: boolean, message?: string) => void;

class LoadingService {
  private listeners: Set<LoadingListener> = new Set();
  private loadingCount = 0;
  private currentMessage = '';

  /**
   * Show global loader
   */
  show(message = 'Loading...'): void {
    this.loadingCount++;
    this.currentMessage = message;
    this.notifyListeners(true, message);
  }

  /**
   * Hide global loader
   */
  hide(): void {
    this.loadingCount = Math.max(0, this.loadingCount - 1);
    
    if (this.loadingCount === 0) {
      this.currentMessage = '';
      this.notifyListeners(false);
    }
  }

  /**
   * Execute async function with loading state
   */
  async withLoading<T>(
    asyncFn: () => Promise<T>,
    message = 'Loading...'
  ): Promise<T> {
    this.show(message);
    try {
      return await asyncFn();
    } finally {
      this.hide();
    }
  }

  /**
   * Subscribe to loading state changes
   */
  subscribe(listener: LoadingListener): () => void {
    this.listeners.add(listener);
    
    // Immediately notify with current state
    listener(this.loadingCount > 0, this.currentMessage);
    
    // Return unsubscribe function
    return () => {
      this.listeners.delete(listener);
    };
  }

  /**
   * Get current loading state
   */
  isLoading(): boolean {
    return this.loadingCount > 0;
  }

  /**
   * Notify all listeners
   */
  private notifyListeners(isLoading: boolean, message?: string): void {
    this.listeners.forEach(listener => listener(isLoading, message));
  }
}

// Singleton instance
export const loadingService = new LoadingService();
