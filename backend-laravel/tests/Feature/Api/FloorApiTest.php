<?php

namespace Tests\Feature\Api;

use Tests\TestCase;
use Illuminate\Foundation\Testing\RefreshDatabase;

class FloorApiTest extends TestCase
{
    use RefreshDatabase;

    /**
     * Test floors index endpoint
     */
    public function test_can_get_floors_list(): void
    {
        $response = $this->getJson('/api/v1/floors');
        
        $response->assertStatus(200);
        // Accept any valid JSON response
        $this->assertIsArray($response->json());
    }

    /**
     * Test can get single floor
     */
    public function test_can_get_single_floor(): void
    {
        // Create a floor first
        $floor = \App\Models\Floor::factory()->create();
        
        $response = $this->getJson("/api/v1/floors/{$floor->id}");
        
        $response->assertStatus(200);
    }
}
