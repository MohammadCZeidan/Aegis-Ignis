<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\CreateFireAlertRequest;
use App\Http\Requests\ResolveAlertRequest;
use App\Services\EmergencyService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class EmergencyController extends Controller
{
    public function __construct(
        private readonly EmergencyService $emergencyService
    ) {
    }

    public function createFireAlert(CreateFireAlertRequest $request): JsonResponse
    {
        $alert = $this->emergencyService->createFireAlert($request->validated());
        
        if (!$alert) {
            return response()->json([
                'success' => false,
                'message' => 'Detection rejected - confidence too low (< 30%)',
                'confidence' => $request->validated()['confidence']
            ], 400);
        }

        return response()->json([
            'success' => true,
            'message' => 'Fire alert created',
            'alert' => $alert,
            'ai_message' => $alert->ai_message
        ]);
    }

    public function getActiveAlerts(Request $request): JsonResponse
    {
        $perPage = $request->input('per_page', 10);
        $alerts = $this->emergencyService->getActiveAlerts($perPage);

        return response()->json($alerts);
    }

    public function getAlertHistory(Request $request): JsonResponse
    {
        $perPage = $request->input('per_page', 15);
        $severity = $request->input('severity');
        $floorId = $request->input('floor_id');

        $alerts = $this->emergencyService->getAlertHistory($perPage, $severity, $floorId);

        return response()->json($alerts);
    }

    public function acknowledgeAlert(int $id): JsonResponse
    {
        $this->emergencyService->acknowledgeAlert($id);

        return response()->json([
            'success' => true,
            'message' => 'Alert acknowledged'
        ]);
    }

    public function resolveAlert(ResolveAlertRequest $request, int $id): JsonResponse
    {
        $isFalseAlarm = $request->validated()['is_false_alarm'] ?? false;
        $this->emergencyService->resolveAlert($id, $isFalseAlarm);

        return response()->json([
            'success' => true,
            'message' => 'Alert resolved'
        ]);
    }
}
