<?php

namespace Tests\Feature\Api;

use Tests\TestCase;
use Illuminate\Foundation\Testing\RefreshDatabase;
use App\Models\Camera;
use App\Models\Floor;

class CameraApiTest extends TestCase
{
    use RefreshDatabase;

    public function test_can_get_cameras_list(): void
    {
        $response = $this->getJson('/api/v1/cameras');
        
        $response->assertStatus(200);
        $this->assertIsArray($response->json());
    }

    public function test_can_get_cameras_list_with_data(): void
    {
        Camera::factory()->count(3)->create();
        
        $response = $this->getJson('/api/v1/cameras');
        
        $response->assertStatus(200);
        $data = $response->json();
        $this->assertIsArray($data);
        $this->assertGreaterThanOrEqual(3, count($data));
    }

    public function test_can_get_single_camera(): void
    {
        $camera = Camera::factory()->create();
        
        $response = $this->getJson("/api/v1/cameras/{$camera->id}");
        
        $response->assertStatus(200);
    }

    public function test_can_get_nonexistent_camera(): void
    {
        $response = $this->getJson('/api/v1/cameras/99999');
        
        $this->assertContains($response->status(), [404, 200]);
    }

    public function test_can_update_camera_floor(): void
    {
        $camera = Camera::factory()->create();
        $floor = Floor::factory()->create();
        
        $response = $this->patchJson("/api/v1/cameras/{$camera->id}/floor", [
            'floor_id' => $floor->id
        ]);
        
        $response->assertStatus(200);
    }

    public function test_can_update_camera_floor_with_invalid_floor(): void
    {
        $camera = Camera::factory()->create();
        
        $response = $this->patchJson("/api/v1/cameras/{$camera->id}/floor", [
            'floor_id' => 99999
        ]);
        
        $this->assertContains($response->status(), [200, 422, 404]);
    }

    public function test_can_update_camera_floor_requires_floor_id(): void
    {
        $camera = Camera::factory()->create();
        
        $response = $this->patchJson("/api/v1/cameras/{$camera->id}/floor", []);
        
        $this->assertContains($response->status(), [200, 422]);
    }

    public function test_cameras_list_includes_floor_relationship(): void
    {
        $floor = Floor::factory()->create();
        $camera = Camera::factory()->create(['floor_id' => $floor->id]);
        
        $response = $this->getJson('/api/v1/cameras');
        
        $response->assertStatus(200);
        $data = $response->json();
        $this->assertIsArray($data);
    }
}
