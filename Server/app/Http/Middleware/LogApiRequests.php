<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Log;
use Symfony\Component\HttpFoundation\Response;

/**
 * Log all API requests and responses
 */
class LogApiRequests
{
    public function handle(Request $request, Closure $next): Response
    {
        $startTime = microtime(true);
            Log::info('API Request', [
            'method' => $request->method(),
            'url' => $request->fullUrl(),
            'ip' => $request->ip(),
            'user_agent' => $request->userAgent(),
            'user_id' => $request->user()?->id,
        ]);
        
        // Process request
        $response = $next($request);
        
        // Log response
        $duration = round((microtime(true) - $startTime) * 1000, 2);
        
        Log::info('API Response', [
            'method' => $request->method(),
            'url' => $request->fullUrl(),
            'status' => $response->getStatusCode(),
            'duration_ms' => $duration,
        ]);
        
        // Add custom headers
        $response->headers->set('X-Response-Time', $duration . 'ms');
        $response->headers->set('X-API-Version', 'v1');
        
        return $response;
    }
}
