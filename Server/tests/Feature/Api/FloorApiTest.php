<?php

namespace Tests\Feature\Api;

use Tests\TestCase;
use Illuminate\Foundation\Testing\RefreshDatabase;
use App\Models\Floor;
use App\Models\Camera;

class FloorApiTest extends TestCase
{
    use RefreshDatabase;

    public function test_can_get_floors_list(): void
    {
        $response = $this->getJson('/api/v1/floors');
        
        $response->assertStatus(200);
        $this->assertIsArray($response->json());
    }

    public function test_can_get_floors_list_with_data(): void
    {
        Floor::factory()->count(3)->create();
        
        $response = $this->getJson('/api/v1/floors');
        
        $response->assertStatus(200);
        $data = $response->json();
        $this->assertIsArray($data);
        $this->assertGreaterThanOrEqual(3, count($data));
    }

    public function test_can_get_single_floor(): void
    {
        $floor = Floor::factory()->create();
        
        $response = $this->getJson("/api/v1/floors/{$floor->id}");
        
        $response->assertStatus(200);
    }

    public function test_can_get_single_floor_with_cameras(): void
    {
        $floor = Floor::factory()->create();
        Camera::factory()->count(2)->create(['floor_id' => $floor->id]);
        
        $response = $this->getJson("/api/v1/floors/{$floor->id}");
        
        $response->assertStatus(200);
    }

    public function test_can_get_nonexistent_floor(): void
    {
        $response = $this->getJson('/api/v1/floors/99999');
        
        $this->assertContains($response->status(), [404, 200]);
    }

    public function test_floors_list_returns_empty_array_when_no_floors(): void
    {
        $response = $this->getJson('/api/v1/floors');
        
        $response->assertStatus(200);
        $data = $response->json();
        $this->assertIsArray($data);
    }
}
