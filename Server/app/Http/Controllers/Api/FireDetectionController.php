<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\ReportFireDetectionRequest;
use App\Services\FireDetectionService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class FireDetectionController extends Controller
{
    private FireDetectionService $fireDetectionService;

    public function __construct(FireDetectionService $fireDetectionService)
    {
        $this->fireDetectionService = $fireDetectionService;
    }

    public function reportDetection(ReportFireDetectionRequest $request): JsonResponse
    {
        $result = $this->fireDetectionService->reportDetection($request->validated());

        return response()->json([
            'success' => true,
            'fire_event_id' => $result['fire_event']->id ?? null,
            'alert_id' => $result['alert']->id ?? null,
            'data' => $result['data'] ?? null,
        ], 201);
    }

    public function index(Request $request): JsonResponse
    {
        $filters = $this->extractFiltersFromRequest($request);
        $events = $this->fireDetectionService->getAllFireEvents(
            $filters['floor_id'], 
            $filters['is_resolved']
        );

        return response()->json($events);
    }

    public function show($id): JsonResponse
    {
        $event = $this->fireDetectionService->getFireEventById((int) $id);

        return response()->json($event);
    }

    public function resolve(Request $request, $id): JsonResponse
    {
        $event = $this->fireDetectionService->resolveFireEvent((int) $id);

        return response()->json($event);
    }

    private function extractFiltersFromRequest(Request $request): array
    {
        return [
            'floor_id' => $request->has('floor_id') ? (int) $request->floor_id : null,
            'is_resolved' => $request->has('is_resolved') ? 
                filter_var($request->is_resolved, FILTER_VALIDATE_BOOLEAN) : null,
        ];
    }
}

