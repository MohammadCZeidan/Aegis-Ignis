<?php

namespace App\Services\Gateway;

use Illuminate\Http\UploadedFile;
use Illuminate\Support\Facades\Log;

/**
 * Client for Python Face Detection Microservice
 */
class FaceServiceClient extends MicroserviceClient
{
    public function __construct()
    {
        parent::__construct();
        
        $this->serviceName = 'face-service';
        $this->baseUrl = config('services.microservices.face_service_url', 'http://localhost:8001');
    }

    /**
     * Detect face and extract embedding from photo
     *
     * @param UploadedFile|string $photo File upload or file path
     * @return array{success: bool, embedding: array|null, confidence: float|null, bounding_box: array|null, error: string|null}
     */
    public function detectFace($photo): array
    {
        try {
            $multipart = [];
            
            if ($photo instanceof UploadedFile) {
                $multipart[] = [
                    'name' => 'photo',
                    'contents' => fopen($photo->getPathname(), 'r'),
                    'filename' => $photo->getClientOriginalName()
                ];
            } elseif (is_string($photo) && file_exists($photo)) {
                $multipart[] = [
                    'name' => 'photo',
                    'contents' => fopen($photo, 'r'),
                    'filename' => basename($photo)
                ];
            } else {
                throw new MicroserviceClientException('Invalid photo format. Must be UploadedFile or valid file path.');
            }

            $response = $this->request('post', '/detect-face', [
                'multipart' => $multipart
            ]);

            Log::info('Face detection successful', [
                'confidence' => $response['confidence'] ?? null,
                'has_embedding' => isset($response['embedding'])
            ]);

            return [
                'success' => $response['success'] ?? false,
                'embedding' => $response['embedding'] ?? null,
                'confidence' => $response['confidence'] ?? null,
                'bounding_box' => $response['bounding_box'] ?? null,
                'error' => $response['error'] ?? null
            ];

        } catch (MicroserviceUnavailableException $e) {
            Log::error('Face service unavailable', [
                'error' => $e->getMessage()
            ]);
            
            return [
                'success' => false,
                'embedding' => null,
                'confidence' => null,
                'bounding_box' => null,
                'error' => 'Face detection service is currently unavailable. Please try again later.'
            ];
            
        } catch (Exception $e) {
            Log::error('Face detection failed', [
                'error' => $e->getMessage(),
                'trace' => $e->getTraceAsString()
            ]);
            
            return [
                'success' => false,
                'embedding' => null,
                'confidence' => null,
                'bounding_box' => null,
                'error' => 'Failed to process face detection: ' . $e->getMessage()
            ];
        }
    }

    /**
     * Extract embedding from base64 image
     *
     * @param string $base64Image Base64 encoded image
     * @return array
     */
    public function detectFaceFromBase64(string $base64Image): array
    {
        // Decode base64 and save to temp file
        $imageData = base64_decode(preg_replace('#^data:image/\w+;base64,#i', '', $base64Image));
        $tempFile = tempnam(sys_get_temp_dir(), 'face_') . '.jpg';
        file_put_contents($tempFile, $imageData);

        try {
            $result = $this->detectFace($tempFile);
            return $result;
        } finally {
            // Clean up temp file
            if (file_exists($tempFile)) {
                unlink($tempFile);
            }
        }
    }

    /**
     * Compare two face embeddings (cosine similarity)
     *
     * @param array $embedding1 First face embedding
     * @param array $embedding2 Second face embedding
     * @return float Similarity score (0-1, higher is more similar)
     */
    public function compareFaces(array $embedding1, array $embedding2): float
    {
        if (count($embedding1) !== count($embedding2)) {
            throw new MicroserviceClientException('Embeddings must have the same dimension');
        }

        // Cosine similarity
        $dotProduct = 0;
        $magnitude1 = 0;
        $magnitude2 = 0;

        for ($i = 0; $i < count($embedding1); $i++) {
            $dotProduct += $embedding1[$i] * $embedding2[$i];
            $magnitude1 += $embedding1[$i] ** 2;
            $magnitude2 += $embedding2[$i] ** 2;
        }

        $magnitude1 = sqrt($magnitude1);
        $magnitude2 = sqrt($magnitude2);

        if ($magnitude1 == 0 || $magnitude2 == 0) {
            return 0;
        }

        return $dotProduct / ($magnitude1 * $magnitude2);
    }
}
