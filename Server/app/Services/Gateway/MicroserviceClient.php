<?php

namespace App\Services\Gateway;

use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Cache;
use Exception;

/**
 * Base class for microservice communication with retry logic and circuit breaker pattern
 */
abstract class MicroserviceClient
{
    protected string $baseUrl;
    protected int $timeout;
    protected int $maxRetries;
    protected int $retryDelay; // milliseconds
    protected string $serviceName;
    
    public function __construct()
    {
        $this->timeout = config('services.microservices.timeout', 10);
        $this->maxRetries = config('services.microservices.max_retries', 3);
        $this->retryDelay = config('services.microservices.retry_delay', 100);
    }

    /**
     * Make HTTP request with retry logic and circuit breaker
     */
    protected function request(string $method, string $endpoint, array $options = []): mixed
    {
        // Check circuit breaker
        if ($this->isCircuitOpen()) {
            throw new MicroserviceUnavailableException(
                "{$this->serviceName} is currently unavailable (circuit open)"
            );
        }

        $attempt = 0;
        $lastException = null;

        while ($attempt < $this->maxRetries) {
            try {
                $response = Http::timeout($this->timeout)
                    ->withOptions(['verify' => false]) // For local development
                    ->{$method}($this->baseUrl . $endpoint, $options);

                if ($response->successful()) {
                    $this->recordSuccess();
                    return $response->json();
                }

                // Non-successful but valid HTTP response
                if ($response->clientError()) {
                    // 4xx errors shouldn't be retried
                    Log::warning("{$this->serviceName} client error", [
                        'endpoint' => $endpoint,
                        'status' => $response->status(),
                        'body' => $response->body()
                    ]);
                    throw new MicroserviceClientException(
                        "Client error: {$response->status()}",
                        $response->status()
                    );
                }

                // 5xx errors should be retried
                throw new MicroserviceServerException(
                    "Server error: {$response->status()}",
                    $response->status()
                );

            } catch (Exception $e) {
                $lastException = $e;
                $attempt++;
                
                Log::warning("{$this->serviceName} request failed", [
                    'endpoint' => $endpoint,
                    'attempt' => $attempt,
                    'error' => $e->getMessage()
                ]);

                if ($attempt < $this->maxRetries) {
                    usleep($this->retryDelay * 1000 * $attempt); // Exponential backoff
                }
            }
        }

        // All retries exhausted
        $this->recordFailure();
        
        Log::error("{$this->serviceName} request failed after all retries", [
            'endpoint' => $endpoint,
            'attempts' => $attempt,
            'error' => $lastException->getMessage()
        ]);

        throw new MicroserviceUnavailableException(
            "{$this->serviceName} is unavailable after {$attempt} attempts",
            0,
            $lastException
        );
    }

    /**
     * Check if circuit breaker is open (service is marked as down)
     */
    protected function isCircuitOpen(): bool
    {
        $failures = Cache::get($this->getCircuitKey(), 0);
        $threshold = config('services.microservices.circuit_breaker_threshold', 5);
        
        return $failures >= $threshold;
    }

    /**
     * Record successful request (reset circuit breaker)
     */
    protected function recordSuccess(): void
    {
        Cache::forget($this->getCircuitKey());
    }

    /**
     * Record failed request (increment circuit breaker)
     */
    protected function recordFailure(): void
    {
        $key = $this->getCircuitKey();
        $failures = Cache::get($key, 0) + 1;
        $ttl = config('services.microservices.circuit_breaker_ttl', 60); // seconds
        
        Cache::put($key, $failures, $ttl);
    }

    /**
     * Get circuit breaker cache key
     */
    protected function getCircuitKey(): string
    {
        return "circuit_breaker:{$this->serviceName}";
    }

    /**
     * Check if service is healthy
     */
    public function healthCheck(): bool
    {
        try {
            $response = Http::timeout(5)->get($this->baseUrl . '/health');
            return $response->successful();
        } catch (Exception $e) {
            Log::warning("{$this->serviceName} health check failed", [
                'error' => $e->getMessage()
            ]);
            return false;
        }
    }

    /**
     * Reset circuit breaker (for manual intervention)
     */
    public function resetCircuit(): void
    {
        Cache::forget($this->getCircuitKey());
        Log::info("{$this->serviceName} circuit breaker manually reset");
    }
}
