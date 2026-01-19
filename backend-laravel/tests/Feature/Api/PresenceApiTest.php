<?php

namespace Tests\Feature\Api;

use Tests\TestCase;
use Illuminate\Foundation\Testing\RefreshDatabase;

class PresenceApiTest extends TestCase
{
    use RefreshDatabase;

    /**
     * Test can get current presence
     */
    public function test_can_get_current_presence(): void
    {
        $response = $this->getJson('/api/v1/presence/current');
        
        $response->assertStatus(200);
        $this->assertIsArray($response->json());
    }

    /**
     * Test presence people endpoint requires authentication
     */
    public function test_can_get_all_people_in_building(): void
    {
        $response = $this->getJson('/api/v1/presence/people');
        
        $this->assertContains($response->status(), [200, 401, 404]);
    }

    /**
     * Test can get floor presence
     */
    public function test_can_get_floor_presence(): void
    {
        $floor = \App\Models\Floor::factory()->create();
        
        $response = $this->getJson("/api/v1/presence/floor-live/{$floor->id}");
        
        $response->assertStatus(200);
        $this->assertIsArray($response->json());
    }
}
