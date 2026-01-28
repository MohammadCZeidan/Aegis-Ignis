<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\CheckFaceDuplicateRequest;
use App\Http\Requests\CreateEmployeeRequest;
use App\Http\Requests\IdentifyFaceRequest;
use App\Http\Requests\RegisterFaceEmbeddingRequest;
use App\Http\Requests\RegisterFaceRequest;
use App\Services\EmployeeService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use GuzzleHttp\Exception\RequestException;

class EmployeeController extends Controller
{
    public function __construct(
        private readonly EmployeeService $employeeService
    ) {
    }
    public function index(Request $request): JsonResponse
    {
        $employees = \App\Models\Employee::with('floor')->get();
        
        return response()->json([
            'employees' => $employees,
            'total' => $employees->count(),
        ]);
    }

    public function byFloor(int $floorId): JsonResponse
    {
        $employees = $this->employeeService->getEmployeesByFloor($floorId);

        return response()->json([
            'employees' => $this->employeeService->formatEmployeesResponse($employees),
            'total' => $employees->count(),
        ]);
    }

    public function registerFaceEmbedding(RegisterFaceEmbeddingRequest $request, int $employeeId): JsonResponse
    {
        $employee = $this->employeeService->registerFaceEmbedding($employeeId, $request->validated());

        return response()->json([
            'success' => true,
            'message' => 'Face registered successfully' . (isset($request->embedding) ? '' : ' (without embeddings)'),
            'employee' => [
                'id' => $employee->id,
                'name' => $employee->name,
                'face_registered_at' => $employee->face_registered_at,
                'has_embedding' => isset($request->embedding)
            ]
        ]);
    }

    public function getRegisteredFaces(): JsonResponse
    {
        $employees = $this->employeeService->getRegisteredFaces();

        return response()->json([
            'success' => true,
            'data' => $employees,
            'count' => $employees->count()
        ])
        ->header('Cache-Control', 'public, max-age=30')
        ->header('X-Total-Count', $employees->count())
        ->header('X-Cache-Hit', \Cache::has('registered_faces') ? 'true' : 'false');
    }

    public function registerFace(RegisterFaceRequest $request): JsonResponse
    {
        try {
            $employee = $this->employeeService->registerEmployeeWithFace(
                $request->validated(),
                $request->file('photo')
            );

            return response()->json(
                $this->employeeService->formatEmployeeResponse($employee),
                201
            );
        } catch (\Exception $e) {
            return response()->json([
                'detail' => 'Error processing image: ' . $e->getMessage()
            ], 500);
        }
    }

    public function createForFaceRegistration(CreateEmployeeRequest $request): JsonResponse
    {
        try {
            $employee = $this->employeeService->createEmployee($request->validated());

            return response()->json([
                'success' => true,
                'id' => $employee->id,
                'employee_id' => $employee->id,
                'name' => $employee->name,
                'employee_number' => $employee->employee_number,
                'message' => 'Employee created successfully'
            ], 201);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'detail' => 'Error creating employee: ' . $e->getMessage()
            ], 500);
        }
    }

    public function getNextEmployeeId(): JsonResponse
    {
        try {
            $nextId = $this->employeeService->getNextEmployeeId();

            return response()->json([
                'success' => true,
                'next_id' => $nextId
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'detail' => 'Error generating employee ID: ' . $e->getMessage()
            ], 500);
        }
    }

    public function checkFaceDuplicate(CheckFaceDuplicateRequest $request): JsonResponse
    {
        try {
            $result = $this->employeeService->checkFaceDuplicate($request->file('image'));

            return response()->json([
                'success' => true,
                'is_duplicate' => $result['is_duplicate'] ?? false,
                'matched_employee' => $result['matched_employee'] ?? null,
                'similarity' => $result['similarity'] ?? null,
                'message' => $result['message'] ?? 'Face check completed'
            ]);
        } catch (RequestException $e) {
            $statusCode = $e->getResponse() ? $e->getResponse()->getStatusCode() : 500;
            $responseBody = $e->getResponse() ? $e->getResponse()->getBody()->getContents() : null;
            
            if ($statusCode === 400 && $responseBody) {
                $error = json_decode($responseBody, true);
                return response()->json([
                    'success' => false,
                    'is_duplicate' => true,
                    'detail' => $error['detail'] ?? 'Face is already registered'
                ], 400);
            }
            
            if ($statusCode === 503) {
                return response()->json([
                    'success' => false,
                    'service_unavailable' => true,
                    'detail' => 'Face recognition service is currently unavailable. Please try again later or contact support.'
                ], 503);
            }

            return response()->json([
                'success' => false,
                'detail' => 'Error checking face: ' . $e->getMessage()
            ], 500);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'detail' => 'Error processing image: ' . $e->getMessage()
            ], 500);
        }
    }

    public function identifyFace(IdentifyFaceRequest $request): JsonResponse
    {
        try {
            $threshold = $request->validated()['threshold'] ?? 0.6;
            $result = $this->employeeService->identifyFace(
                $request->validated()['embedding'],
                $threshold
            );
            
            return response()->json($result);
        } catch (\Exception $e) {
            return response()->json([
                'matched' => false,
                'error' => 'Error identifying face: ' . $e->getMessage()
            ], 500);
        }
    }

    public function destroy(Request $request, int $id): JsonResponse
    {
        if ($request->user()->role !== 'admin') {
            return response()->json([
                'detail' => 'Only admins can delete employees'
            ], 403);
        }

        $this->employeeService->deleteEmployee($id);

        return response()->json(null, 204);
    }
}

