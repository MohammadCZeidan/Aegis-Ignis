<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\StoreCameraRequest;
use App\Http\Requests\UpdateCameraFloorRequest;
use App\Http\Requests\UpdateCameraRequest;
use App\Services\CameraService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class CameraController extends Controller
{
    private CameraService $cameraService;

    public function __construct(CameraService $cameraService)
    {
        $this->cameraService = $cameraService;
    }
    public function index(Request $request): JsonResponse
    {
        $floorId = $this->extractFloorIdFromRequest($request);
        $cameras = $this->cameraService->getAllCameras($floorId);

        return response()->json($cameras);
    }

    public function show($id): JsonResponse
    {
        $camera = $this->cameraService->getCameraById((int) $id);

        return response()->json($camera);
    }

    public function store(StoreCameraRequest $request): JsonResponse
    {
        $camera = $this->cameraService->createCamera($request->validated());

        return response()->json($camera->load('floor'), 201);
    }

    public function update(UpdateCameraRequest $request, $id): JsonResponse
    {
        $camera = $this->cameraService->updateCamera((int) $id, $request->validated());

        return response()->json($camera);
    }

    public function destroy(UpdateCameraRequest $request, $id): JsonResponse
    {
        $this->cameraService->deleteCamera((int) $id);

        return response()->json(null, 204);
    }

    public function updateFloor(UpdateCameraFloorRequest $request, $id): JsonResponse
    {
        $updateResult = $this->cameraService->updateCameraFloor(
            (int) $id, 
            $request->validated()['floor_id']
        );

        return response()->json($updateResult);
    }

    public function updateAlertsFloor(Request $request, $id): JsonResponse
    {
        $floorId = $request->input('floor_id');
        
        if (!$floorId) {
            return response()->json(['error' => 'floor_id is required'], 400);
        }

        // Update all alerts for this camera to the new floor
        $updatedCount = \App\Models\Alert::where('camera_id', $id)
            ->update(['floor_id' => $floorId]);

        return response()->json([
            'success' => true,
            'camera_id' => $id,
            'new_floor_id' => $floorId,
            'updated_alerts' => $updatedCount
        ]);
    }

    private function extractFloorIdFromRequest(Request $request): ?int
    {
        return $request->has('floor_id') ? (int) $request->floor_id : null;
    }
}
