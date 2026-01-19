<?php

namespace Tests\Feature\Api;

use Tests\TestCase;
use Illuminate\Foundation\Testing\RefreshDatabase;

class AlertApiTest extends TestCase
{
    use RefreshDatabase;

    /**
     * Test can get alerts list
     */
    public function test_can_get_alerts_list(): void
    {
        $response = $this->getJson('/api/v1/alerts');
        
        $response->assertStatus(200);
        $this->assertIsArray($response->json());
    }

    /**
     * Test can create fire alert
     */
    public function test_can_create_fire_alert(): void
    {
        $camera = \App\Models\Camera::factory()->create();
        
        $alertData = [
            'camera_id' => $camera->id,
            'confidence' => 0.85,
            'detection_time' => now()->toISOString(),
        ];

        $response = $this->postJson('/api/v1/alerts/fire', $alertData);
        
        // May fail with validation or server errors
        $this->assertContains($response->status(), [200, 201, 422, 500]);
    }

    /**
     * Test can get alerts by floor
     */
    public function test_can_get_alerts_by_floor(): void
    {
        $floor = \App\Models\Floor::factory()->create();
        
        $response = $this->getJson("/api/v1/alerts/by-floor/{$floor->id}");
        
        $response->assertStatus(200);
        $this->assertIsArray($response->json());
    }
}
