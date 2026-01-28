<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\StoreFloorRequest;
use App\Http\Requests\UpdateFloorRequest;
use App\Services\FloorService;

class FloorController extends Controller
{
    protected FloorService $floorService;

    public function __construct(FloorService $floorService)
    {
        $this->floorService = $floorService;
    }

    /**
     * List all floors
     */
    public function index()
    {
        $floors = $this->floorService->getAllFloors();
        return response()->json($floors);
    }

    /**
     * Get floor details
     */
    public function show($id)
    {
        $floor = $this->floorService->getFloorById((int) $id);

        return response()->json($floor);
    }

    /**
     * Create a new floor
     */
    public function store(StoreFloorRequest $request)
    {
        $floor = $this->floorService->createFloor($request->validated());

        return response()->json($floor->load('building'), 201);
    }

    /**
     * Update floor
     */
    public function update(UpdateFloorRequest $request, $id)
    {
        $floor = $this->floorService->updateFloor((int) $id, $request->validated());

        return response()->json($floor);
    }

    /**
     * Delete floor
     */
    public function destroy($id)
    {
        try {
            $this->floorService->deleteFloor((int) $id);
            return response()->json(['message' => 'Floor deleted successfully'], 200);
        } catch (\Exception $e) {
            return response()->json(['error' => 'Failed to delete floor: ' . $e->getMessage()], 500);
        }
    }
}
