<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Services\AlertService;
use App\Services\AlertCleanupService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class AlertController extends Controller
{
    private AlertService $alertService;
    private AlertCleanupService $cleanupService;

    public function __construct(AlertService $alertService, AlertCleanupService $cleanupService)
    {
        $this->alertService = $alertService;
        $this->cleanupService = $cleanupService;
    }

    public function index(Request $request): JsonResponse
    {
        $filters = $this->extractFiltersFromRequest($request);
        $result = $this->alertService->getAllAlerts($filters);
        
        return response()->json($result);
    }

    public function show($id): JsonResponse
    {
        $result = $this->alertService->getAlertById((int) $id);
        
        $statusCode = $result['success'] ? 200 : 404;
        return response()->json($result, $statusCode);
    }

    public function acknowledge(Request $request, $id): JsonResponse
    {
        $result = $this->alertService->acknowledgeAlert((int) $id);
        
        $statusCode = $result['success'] ? 200 : 500;
        return response()->json($result, $statusCode);
    }

    public function createFireAlert(Request $request): JsonResponse
    {
        $result = $this->alertService->createFireAlert($request->all());
        
        $statusCode = $result['success'] ? 201 : 500;
        return response()->json($result, $statusCode);
    }

    public function byFloor($floorId): JsonResponse
    {
        try {
            $alerts = $this->alertService->getAlertsByFloor((int) $floorId);
            return response()->json($alerts);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'error' => 'Failed to fetch alerts'
            ], 500);
        }
    }

    private function extractFiltersFromRequest(Request $request): array
    {
        $filters = [];
        
        if ($request->has('status')) {
            $filters['status'] = $request->status;
        }
        
        if ($request->has('event_type')) {
            $filters['event_type'] = $request->event_type;
        }
              if ($request->has('floor_id')) {
            $filters['floor_id'] = (int) $request->floor_id;
        }
        
        return $filters;
    }

    public function cleanupImages(Request $request): JsonResponse
    {
        $days = $request->input('days', 1);
        $deleteAll = $request->boolean('all', false);
        
        $result = $this->cleanupService->cleanupImages($days, $deleteAll);
        
        $statusCode = $result['success'] ? 200 : 500;
        return response()->json($result, $statusCode);
    }

    public function cleanupAlerts(Request $request): JsonResponse
    {
        try {
            $days = $request->input('days', 1);
            $deleteAll = $request->boolean('all', false);
            $imagesOnly = $request->boolean('images-only', false);
            
            $command = 'alerts:cleanup';
            $options = [];
            
            if ($deleteAll) {
                $options[] = '--all';
            } else {
                $options[] = "--days={$days}";
            }
            
            if ($imagesOnly) {
                $options[] = '--images-only';
            }
            
            $fullCommand = $command . ' ' . implode(' ', $options);
            
            \Artisan::call($command, [
                '--days' => $deleteAll ? null : $days,
                '--all' => $deleteAll,
                '--images-only' => $imagesOnly
            ]);
            
            $output = \Artisan::output();
            
            \Log::info('Manual alert cleanup triggered', [
                'command' => $fullCommand,
                'output' => $output
            ]);
            
            return response()->json([
                'success' => true,
                'message' => 'Alert cleanup completed successfully',
                'command' => $fullCommand,
                'output' => $output
            ]);
            
        } catch (\Exception $e) {
            \Log::error('Manual alert cleanup failed', [
                'error' => $e->getMessage()
            ]);
            
            return response()->json([
                'success' => false,
                'error' => 'Cleanup failed: ' . $e->getMessage()
            ], 500);
        }
    }
}
