import { useEffect, useState } from 'react';
import { loadingService } from '../services/loadingService';
import { Loader2 } from 'lucide-react';

/**
 * Global Loading Overlay
 * 
 * Shows a full-screen loading overlay when the loading service is active.
 * This component should be placed once at the app root level.
 */
export function GlobalLoader() {
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    const unsubscribe = loadingService.subscribe((loading, msg) => {
      setIsLoading(loading);
      setMessage(msg || 'Loading...');
    });

    return unsubscribe;
  }, []);

  if (!isLoading) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center">
      <div className="bg-white rounded-lg p-6 shadow-xl flex flex-col items-center gap-4 min-w-[200px]">
        <Loader2 className="h-8 w-8 text-blue-600 animate-spin" />
        <p className="text-slate-900 font-medium">{message}</p>
      </div>
    </div>
  );
}
