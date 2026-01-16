<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\ReportFireDetectionRequest;
use App\Services\FireDetectionService;
use Illuminate\Http\Request;

class FireDetectionController extends Controller
{
    protected FireDetectionService $fireDetectionService;

    public function __construct(FireDetectionService $fireDetectionService)
    {
        $this->fireDetectionService = $fireDetectionService;
    }

    /**
     * Report fire detection from live camera feed
     * This endpoint is called by the fire detection service
     */
    public function reportDetection(ReportFireDetectionRequest $request)
    {
        $result = $this->fireDetectionService->reportDetection($request->validated());

        return response()->json([
            'success' => true,
            'fire_event_id' => $result['fire_event']->id ?? null,
            'alert_id' => $result['alert']->id ?? null,
            'data' => $result['data'] ?? null,
        ], 201);
    }

    /**
     * Get fire events
     */
    public function index(Request $request)
    {
        $floorId = $request->has('floor_id') ? (int) $request->floor_id : null;
        $isResolved = $request->has('is_resolved') ? filter_var($request->is_resolved, FILTER_VALIDATE_BOOLEAN) : null;

        $events = $this->fireDetectionService->getAllFireEvents($floorId, $isResolved);

        return response()->json($events);
    }

    /**
     * Get fire event details
     */
    public function show($id)
    {
        $event = $this->fireDetectionService->getFireEventById((int) $id);

        return response()->json($event);
    }

    /**
     * Resolve fire event
     */
    public function resolve(Request $request, $id)
    {
        $event = $this->fireDetectionService->resolveFireEvent((int) $id);

        return response()->json($event);
    }
}

