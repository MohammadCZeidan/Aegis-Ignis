<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\StoreCameraRequest;
use App\Http\Requests\UpdateCameraFloorRequest;
use App\Http\Requests\UpdateCameraRequest;
use App\Services\CameraService;
use Illuminate\Http\Request;

class CameraController extends Controller
{
    protected CameraService $cameraService;

    public function __construct(CameraService $cameraService)
    {
        $this->cameraService = $cameraService;
    }

    /**
     * List all cameras
     */
    public function index(Request $request)
    {
        $floorId = $request->has('floor_id') ? (int) $request->floor_id : null;
        $cameras = $this->cameraService->getAllCameras($floorId);

        return response()->json($cameras);
    }

    /**
     * Get camera details
     */
    public function show($id)
    {
        $camera = $this->cameraService->getCameraById((int) $id);

        return response()->json($camera);
    }

    /**
     * Create a new camera
     */
    public function store(StoreCameraRequest $request)
    {
        $camera = $this->cameraService->createCamera($request->validated());

        return response()->json($camera->load('floor'), 201);
    }

    /**
     * Update camera
     */
    public function update(UpdateCameraRequest $request, $id)
    {
        $camera = $this->cameraService->updateCamera((int) $id, $request->validated());

        return response()->json($camera);
    }

    /**
     * Delete camera
     */
    public function destroy(UpdateCameraRequest $request, $id)
    {
        $this->cameraService->deleteCamera((int) $id);

        return response()->json(null, 204);
    }

    /**
     * Update camera floor assignment
     */
    public function updateFloor(UpdateCameraFloorRequest $request, $id)
    {
        $camera = $this->cameraService->updateCamera((int) $id, [
            'floor_id' => $request->validated()['floor_id']
        ]);

        return response()->json([
            'success' => true,
            'message' => "Camera floor updated to {$camera->floor->name}",
            'camera' => $camera
        ]);
    }
}
