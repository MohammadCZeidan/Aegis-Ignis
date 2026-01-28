<?php

namespace App\Services;

use App\Services\Gateway\FaceServiceClient;
use Illuminate\Http\UploadedFile;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Storage;

class FaceRecognitionService
{
    protected $employeeEmbeddings = [];
    protected FaceServiceClient $faceServiceClient;

    public function __construct(FaceServiceClient $faceServiceClient)
    {
        $this->faceServiceClient = $faceServiceClient;
    }

  
    public function detectAndExtractFace(UploadedFile $image): ?array
    {
        $result = $this->faceServiceClient->detectFace($image);
        
        if ($result['success'] && $result['embedding']) {
            return [
                'embedding' => $result['embedding'],
                'confidence' => $result['confidence'] ?? 0.95,
                'bounding_box' => $result['bounding_box'] ?? null,
            ];
        }
        
        if ($result['error']) {
            Log::error('Face detection failed', ['error' => $result['error']]);
        }
        
        return null;
    }

    /**
     * Register employee face embedding
     */
    public function registerEmployee(int $employeeId, string $name, array $embedding): void
    {
        $this->employeeEmbeddings[$employeeId] = [
            'name' => $name,
            'embedding' => $embedding,
        ];
    }

    /**
     * Unregister employee
     */
    public function unregisterEmployee(int $employeeId): void
    {
        unset($this->employeeEmbeddings[$employeeId]);
    }

    /**
     * Identify face from embedding
     */
    public function identifyFace(array $embedding, float $threshold = 0.7): ?array
    {
        $bestMatch = null;
        $bestSimilarity = 0.0;

        foreach ($this->employeeEmbeddings as $employeeId => $data) {
            $similarity = $this->cosineSimilarity($embedding, $data['embedding']);
            
            if ($similarity > $bestSimilarity && $similarity >= $threshold) {
                $bestSimilarity = $similarity;
                $bestMatch = [
                    'employee_id' => $employeeId,
                    'name' => $data['name'],
                    'confidence' => $similarity,
                ];
            }
        }

        return $bestMatch;
    }

    /**
     * Check if face embedding already exists in database (duplicate detection)
     * Returns the duplicate employee info if found, null otherwise
     */
    public function checkForDuplicate(array $newEmbedding, float $threshold = 0.50): ?array
    {
        // Get all employees with face embeddings from database
        $employees = \App\Models\Employee::whereNotNull('face_embedding')->get();
        
        foreach ($employees as $employee) {
            $existingEmbedding = json_decode($employee->face_embedding, true);
            
            if (!$existingEmbedding || !is_array($existingEmbedding)) {
                continue;
            }
            
            $similarity = $this->cosineSimilarity($newEmbedding, $existingEmbedding);
            
            // If similarity is above threshold, this is a duplicate
            if ($similarity >= $threshold) {
                Log::warning('Duplicate face detected!', [
                    'existing_employee' => $employee->name,
                    'similarity' => round($similarity * 100, 2) . '%'
                ]);
                
                return [
                    'employee_id' => $employee->id,
                    'name' => $employee->name,
                    'confidence' => $similarity,
                ];
            }
        }
        
        return null;
    }

    /**
     * Calculate cosine similarity between two vectors
     */
    protected function cosineSimilarity(array $vec1, array $vec2): float
    {
        if (count($vec1) !== count($vec2)) {
            return 0.0;
        }

        $dotProduct = 0.0;
        $norm1 = 0.0;
        $norm2 = 0.0;

        for ($i = 0; $i < count($vec1); $i++) {
            $dotProduct += $vec1[$i] * $vec2[$i];
            $norm1 += $vec1[$i] * $vec1[$i];
            $norm2 += $vec2[$i] * $vec2[$i];
        }

        $norm1 = sqrt($norm1);
        $norm2 = sqrt($norm2);

        if ($norm1 == 0 || $norm2 == 0) {
            return 0.0;
        }

        return $dotProduct / ($norm1 * $norm2);
    }
}

