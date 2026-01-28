<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Services\Gateway\FaceServiceClient;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Redis;

class HealthController extends Controller
{
    /**
     * Overall system health check
     */
    public function index(FaceServiceClient $faceServiceClient)
    {
        $checks = [
            'api' => $this->checkApi(),
            'database' => $this->checkDatabase(),
            'redis' => $this->checkRedis(),
            'face_service' => $this->checkFaceService($faceServiceClient),
        ];
        $allHealthy = collect($checks)->every(fn($check) => $check['status'] === 'healthy');

        return response()->json([
            'status' => $allHealthy ? 'healthy' : 'degraded',
            'timestamp' => now()->toISOString(),
            'checks' => $checks,
        ], $allHealthy ? 200 : 503);
    }

    /**
     * Check API health
     */
    protected function checkApi(): array
    {
        return [
            'status' => 'healthy',
            'message' => 'API is running',
            'version' => 'v1',
        ];
    }

    /**
     * Check database connection
     */
    protected function checkDatabase(): array
    {
        try {
            DB::connection()->getPdo();
            $databaseName = DB::connection()->getDatabaseName();
            
            return [
                'status' => 'healthy',
                'message' => 'Database connected',
                'database' => $databaseName,
            ];
        } catch (\Exception $e) {
            return [
                'status' => 'unhealthy',
                'message' => 'Database connection failed',
                'error' => $e->getMessage(),
            ];
        }
    }

    /**
     * Check Redis connection
     */
    protected function checkRedis(): array
    {
        try {
            Redis::connection()->ping();
            
            return [
                'status' => 'healthy',
                'message' => 'Redis connected',
            ];
        } catch (\Exception $e) {
            return [
                'status' => 'unhealthy',
                'message' => 'Redis connection failed',
                'error' => $e->getMessage(),
            ];
        }
    }

    /**
     * Check Face Service microservice
     */
    protected function checkFaceService(FaceServiceClient $faceServiceClient): array
    {
        try {
            $healthy = $faceServiceClient->healthCheck();
            
            if ($healthy) {
                return [
                    'status' => 'healthy',
                    'message' => 'Face service is responding',
                    'url' => config('services.microservices.face_service_url'),
                ];
            } else {
                return [
                    'status' => 'unhealthy',
                    'message' => 'Face service not responding',
                    'url' => config('services.microservices.face_service_url'),
                ];
            }
        } catch (\Exception $e) {
            return [
                'status' => 'unhealthy',
                'message' => 'Face service check failed',
                'error' => $e->getMessage(),
            ];
        }
    }

    /**
     * Quick health check (just API status, no dependencies)
     */
    public function ping()
    {
        return response()->json([
            'status' => 'ok',
            'timestamp' => now()->toISOString(),
        ]);
    }
}
