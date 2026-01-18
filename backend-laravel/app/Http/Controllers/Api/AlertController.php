<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Services\AlertService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class AlertController extends Controller
{
    private AlertService $alertService;

    public function __construct(AlertService $alertService)
    {
        $this->alertService = $alertService;
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
}
