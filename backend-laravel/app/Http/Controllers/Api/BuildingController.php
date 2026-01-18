<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\UpdateBuildingConfigRequest;
use App\Services\BuildingService;
use Illuminate\Http\JsonResponse;

class BuildingController extends Controller
{
    public function __construct(
        private readonly BuildingService $buildingService
    ) {
    }

    public function getConfig(): JsonResponse
    {
        $building = $this->buildingService->getConfig();
        
        return response()->json([
            'success' => true,
            'data' => $building
        ]);
    }
    
    public function updateConfig(UpdateBuildingConfigRequest $request): JsonResponse
    {
        $building = $this->buildingService->updateConfig($request->validated());
        
        return response()->json([
            'success' => true,
            'message' => 'Building configuration updated successfully',
            'data' => $building
        ]);
    }
    
    public function deleteAllAlerts(): JsonResponse
    {
        try {
            $deletedCount = $this->buildingService->deleteAllAlerts();
            
            return response()->json([
                'success' => true,
                'message' => "Successfully deleted {$deletedCount} alerts and cleared alert images",
                'deleted_count' => $deletedCount
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'error' => 'Failed to delete alerts: ' . $e->getMessage()
            ], 500);
        }
    }
}
