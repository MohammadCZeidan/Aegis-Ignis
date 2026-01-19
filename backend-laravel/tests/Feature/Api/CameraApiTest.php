<?php

namespace Tests\Feature\Api;

use Tests\TestCase;
use Illuminate\Foundation\Testing\RefreshDatabase;

class CameraApiTest extends TestCase
{
    use RefreshDatabase;

    /**
     * Test cameras index endpoint
     */
    public function test_can_get_cameras_list(): void
    {
        $response = $this->getJson('/api/v1/cameras');
        
        $response->assertStatus(200);
        // Accept any valid JSON response
        $this->assertIsArray($response->json());
    }

    /**
     * Test can update camera floor
     */
    public function test_can_update_camera_floor(): void
    {
        $camera = \App\Models\Camera::factory()->create();
        $floor = \App\Models\Floor::factory()->create();
        
        $response = $this->patchJson("/api/v1/cameras/{$camera->id}/floor", [
            'floor_id' => $floor->id
        ]);
        
        $response->assertStatus(200);
    }
}
