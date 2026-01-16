<?php

namespace App\Services;

use App\Models\Employee;
use App\Models\Floor;
use App\Services\FaceRecognitionService;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Facades\Cache;
use GuzzleHttp\Client;

class EmployeeService
{
    protected FaceRecognitionService $faceRecognitionService;

    public function __construct(FaceRecognitionService $faceRecognitionService)
    {
        $this->faceRecognitionService = $faceRecognitionService;
    }

    /**
     * Get all employees with optional filtering
     */
    
    public function getAllEmployees(?int $floorId = null)
    {
        $query = Employee::with('floor');

        if ($floorId) {
            $query->where('floor_id', $floorId);
        }

        return $query->get();
    }

    /**
     * Get employees by floor
     */
    public function getEmployeesByFloor(int $floorId)
    {
        Floor::findOrFail($floorId);

        return Employee::where('floor_id', $floorId)->get();
    }

    /**
     * Register employee with face photo
     */
    public function registerEmployeeWithFace(array $data, $photoFile): Employee
    {
        // Validate floor if provided
        if (isset($data['floor_id']) && $data['floor_id']) {
            Floor::findOrFail($data['floor_id']);
        }

        // Store photo first
        $photoPath = $photoFile->store('employees', 'public');
        $photoUrl = Storage::url($photoPath);

        // Try to process image and detect face (optional - don't fail if service is down)
        $faceEmbedding = null;
        try {
            $faceData = $this->faceRecognitionService->detectAndExtractFace($photoFile);
            
            if ($faceData && isset($faceData['embedding'])) {
                $faceEmbedding = $faceData['embedding'];
                
                // ✅ CHECK FOR DUPLICATE FACE BEFORE REGISTERING
                $duplicate = $this->faceRecognitionService->checkForDuplicate($faceEmbedding);
                if ($duplicate) {
                    // Delete the uploaded photo since we won't use it
                    Storage::disk('public')->delete($photoPath);
                    
                    throw new \Exception(
                        "This face is already registered for employee: {$duplicate['name']} " .
                        "(Similarity: " . round($duplicate['confidence'] * 100, 2) . "%)"
                    );
                }
            }
        } catch (\Exception $e) {
            // If it's our duplicate error, re-throw it
            if (strpos($e->getMessage(), 'already registered') !== false) {
                throw $e;
            }
            
            \Log::warning('Face detection failed during registration, proceeding without embedding', [
                'error' => $e->getMessage()
            ]);
        }

        // Create employee (with or without embedding)
        $employee = Employee::create([
            'name' => $data['name'],
            'email' => $data['email'] ?? null,
            'password' => bcrypt($data['password']),
            'floor_id' => !empty($data['floor_id']) ? $data['floor_id'] : null,
            'face_embedding' => $faceEmbedding,
            'photo_url' => $photoUrl,
        ]);

        // Try to register in face recognition service (optional)
        if ($faceEmbedding) {
            try {
                $this->faceRecognitionService->registerEmployee(
                    $employee->id,
                    $employee->name,
                    $faceEmbedding
                );
            } catch (\Exception $e) {
                \Log::warning('Failed to register employee in face service', [
                    'employee_id' => $employee->id,
                    'error' => $e->getMessage()
                ]);
            }
        }

        return $employee;
    }

    /**
     * Delete employee
     */
    public function deleteEmployee(int $id): void
    {
        $employee = Employee::findOrFail($id);

        // Remove from face recognition service
        $this->faceRecognitionService->unregisterEmployee($employee->id);

        // Delete photo if exists
        if ($employee->photo_url) {
            $path = str_replace('/storage/', '', $employee->photo_url);
            Storage::disk('public')->delete($path);
        }

        $employee->delete();
    }

    /**
     * Format employee data for response
     */
    public function formatEmployeeResponse(Employee $employee): array
    {
        $floorName = null;
        if ($employee->floor_id && $employee->floor) {
            $floorName = $employee->floor->name ?? "Floor {$employee->floor->floor_number}";
        }

        return [
            'id' => $employee->id,
            'name' => $employee->name,
            'email' => $employee->email,
            'floor_id' => $employee->floor_id,
            'floor_name' => $floorName,
            'photo_url' => $employee->photo_url,
            'created_at' => $employee->created_at->toISOString(),
        ];
    }

    /**
     * Format multiple employees for response
     */
    public function formatEmployeesResponse($employees): array
    {
        return $employees->map(function ($employee) {
            return $this->formatEmployeeResponse($employee);
        })->toArray();
    }
    
    public function createEmployee(array $data): Employee
    {
        return Employee::create([
            'name' => $data['name'],
            'employee_number' => $data['employee_number'],
            'department' => $data['department'],
            'email' => $data['email'],
            'password' => bcrypt($data['password']),
            'role' => $data['role'] ?? 'employee',
            'status' => 'active'
        ]);
    }
    
    public function getNextEmployeeId(): string
    {
        $latestEmployee = Employee::whereNotNull('employee_number')
            ->orderBy('id', 'desc')
            ->first();

        if (!$latestEmployee || !$latestEmployee->employee_number) {
            return 'EMP001';
        }

        $currentNumber = (int) substr($latestEmployee->employee_number, 3);
        $nextNumber = $currentNumber + 1;
        
        return 'EMP' . str_pad($nextNumber, 3, '0', STR_PAD_LEFT);
    }
    
    public function registerFaceEmbedding(int $employeeId, array $data): Employee
    {
        $employee = Employee::findOrFail($employeeId);

        $imagePath = $this->storeFaceImage($data['image_data'], $employee->id);

        $updateData = [
            'face_photo_path' => $imagePath,
            'face_registered_at' => now(),
            'face_match_confidence' => $data['confidence'] * 100,
            'current_floor_id' => $data['floor_id'],
            'current_room' => $data['room_location']
        ];
        
        if (isset($data['embedding'])) {
            $updateData['face_embedding'] = json_encode($data['embedding']);
            Cache::forget('registered_faces');
        }
        
        $employee->update($updateData);

        return $employee;
    }
    
    public function getRegisteredFaces()
    {
        return Cache::remember('registered_faces', 30, function () {
            return Employee::whereNotNull('face_embedding')
                ->select('id', 'name', 'employee_number', 'face_embedding')
                ->get();
        });
    }
    
    public function checkFaceDuplicate($imageFile): array
    {
        $pythonServiceUrl = env('PYTHON_FACE_SERVICE_URL', 'http://localhost:8001');
        
        $client = new Client();
        $response = $client->post("$pythonServiceUrl/check-face-duplicate", [
            'multipart' => [
                [
                    'name' => 'file',
                    'contents' => fopen($imageFile->getRealPath(), 'r'),
                    'filename' => $imageFile->getClientOriginalName()
                ]
            ],
            'timeout' => 30
        ]);

        return json_decode($response->getBody()->getContents(), true);
    }
    
    public function identifyFace(array $embedding, float $threshold = 0.6): ?array
    {
        $employees = Employee::whereNotNull('face_embedding')->get();
        
        $bestMatch = null;
        $bestSimilarity = 0;
        
        foreach ($employees as $employee) {
            $storedEmbedding = json_decode($employee->face_embedding, true);
            if (!$storedEmbedding) continue;
            
            $similarity = $this->calculateCosineSimilarity($embedding, $storedEmbedding);
            
            if ($similarity > $bestSimilarity) {
                $bestSimilarity = $similarity;
                $bestMatch = $employee;
            }
        }
        
        if ($bestMatch && $bestSimilarity >= $threshold) {
            return [
                'matched' => true,
                'employee_id' => $bestMatch->id,
                'name' => $bestMatch->name,
                'employee_number' => $bestMatch->employee_number,
                'department' => $bestMatch->department?->name,
                'confidence' => $bestSimilarity,
            ];
        }
        
        return [
            'matched' => false,
            'message' => 'No matching employee found',
            'best_similarity' => $bestSimilarity,
        ];
    }
    
    private function storeFaceImage(string $imageData, int $employeeId): string
    {
        $decodedImage = base64_decode($imageData);
        $filename = 'faces/' . $employeeId . '_' . time() . '.jpg';
        Storage::disk('public')->put($filename, $decodedImage);
        
        return $filename;
    }
    
    private function calculateCosineSimilarity(array $a, array $b): float
    {
        if (count($a) !== count($b)) {
            return 0;
        }
        
        $dotProduct = 0;
        $magnitudeA = 0;
        $magnitudeB = 0;
        
        for ($i = 0; $i < count($a); $i++) {
            $dotProduct += $a[$i] * $b[$i];
            $magnitudeA += $a[$i] * $a[$i];
            $magnitudeB += $b[$i] * $b[$i];
        }
        
        $magnitudeA = sqrt($magnitudeA);
        $magnitudeB = sqrt($magnitudeB);
        
        if ($magnitudeA == 0 || $magnitudeB == 0) {
            return 0;
        }
        
        return $dotProduct / ($magnitudeA * $magnitudeB);
    }
}

