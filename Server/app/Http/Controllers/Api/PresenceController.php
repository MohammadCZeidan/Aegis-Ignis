<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\LogPresenceRequest;
use App\Services\PresenceService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\Log;

class PresenceController extends Controller
{
    public function __construct(
        private readonly PresenceService $presenceService
    ) {
    }

    public function logPresence(LogPresenceRequest $request): JsonResponse
    {
        $log = $this->presenceService->logPresence($request->validated());

        return response()->json([
            'success' => true,
            'message' => 'Presence logged successfully',
            'log' => $log
        ]);
    }

    public function getPeopleByFloor(Request $request, int $floorId): JsonResponse
    {
        try {
            if ($request->input('count_only')) {
                $count = $this->presenceService->getPeopleByFloor($floorId, null, true);
                
                return response()->json([
                    'success' => true,
                    'person_count' => $count
                ]);
            }
            $perPage = $request->input('per_page', 15);
            $employees = $this->presenceService->getPeopleByFloor($floorId, $perPage);

            return response()->json($employees);
        } catch (\Exception $e) {
            \Log::error('Error in getPeopleByFloor', ['error' => $e->getMessage()]);
            return response()->json([
                'success' => true,
                'person_count' => 0,
                'data' => []
            ]);
        }
    }

    public function getAllPeopleInBuilding(Request $request): JsonResponse
    {
        try {
            $perPage = $request->input('per_page', 20);
            $filters = [
                'floor_id' => $request->input('floor_id'),
                'room' => $request->input('room'),
                'search' => $request->input('search'),
            ];

            $employees = $this->presenceService->getAllPeopleInBuilding($perPage, $filters);

            return response()->json([
                'success' => true,
                'data' => $employees
            ]);
        } catch (\Exception $e) {
            \Log::error('Failed to get people in building', ['error' => $e->getMessage()]);
            return response()->json([
                'success' => true,
                'data' => [
                    'data' => [],
                    'total' => 0
                ]
            ]);
        }
    }

    public function getEmployeeDetails(int $id): JsonResponse
    {
        $data = $this->presenceService->getEmployeeDetails($id);
        
        return response()->json($data);
    }

    public function getOccupancyStats(): JsonResponse
    {
        $stats = $this->presenceService->getOccupancyStats();
        
        return response()->json($stats);
    }

    public function logEntry(Request $request): JsonResponse
    {
        try {
            $success = $this->presenceService->logEntry(
                $request->input('employee_name'),
                $request->all()
            );
            
            if (!$success) {
                return response()->json([
                    'success' => false,
                    'error' => 'Employee not found'
                ], 404);
            }

            return response()->json([
                'success' => true,
                'message' => 'Entry logged'
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'error' => $e->getMessage()
            ], 500);
        }
    }

    public function logExit(Request $request): JsonResponse
    {
        try {
            $success = $this->presenceService->logExit(
                $request->input('employee_name'),
                $request->all()
            );
            
            if (!$success) {
                return response()->json([
                    'success' => false,
                    'error' => 'Employee not found'
                ], 404);
            }

            return response()->json([
                'success' => true,
                'message' => 'Exit logged'
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'error' => $e->getMessage()
            ], 500);
        }
    }

    public function getCurrentPresence(): JsonResponse
    {
        try {
            $data = $this->presenceService->getCurrentPresence();
            
            return response()->json([
                'success' => true,
                ...$data
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'error' => $e->getMessage()
            ], 500);
        }
    }

    public function updateFloorPresence(Request $request): JsonResponse
    {
        try {
            $floorId = $request->input('floor_id');
            $people = $request->input('people', []);
            
            // Store in cache for quick retrieval
            Cache::put("floor_presence_{$floorId}", $people, now()->addMinutes(5));
            
            Log::info("Floor presence updated", [
                'floor_id' => $floorId,
                'people_count' => count($people),
                'people' => $people
            ]);
            
            return response()->json([
                'success' => true,
                'message' => 'Floor presence updated',
                'floor_id' => $floorId,
                'count' => count($people)
            ]);
        } catch (\Exception $e) {
            Log::error('Failed to update floor presence', ['error' => $e->getMessage()]);
            return response()->json([
                'success' => false,
                'error' => $e->getMessage()
            ], 500);
        }
    }

    public function getFloorPresence(int $floorId): JsonResponse
    {
        try {
            // Get from cache
            $people = Cache::get("floor_presence_{$floorId}", []);
            
            return response()->json([
                'success' => true,
                'floor_id' => $floorId,
                'people' => $people,
                'count' => count($people),
                'last_updated' => now()->toIso8601String()
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'error' => $e->getMessage()
            ], 500);
        }
    }
}
