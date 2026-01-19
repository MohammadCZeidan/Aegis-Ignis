<?php

namespace Tests\Feature\Api;

use Tests\TestCase;
use Illuminate\Foundation\Testing\RefreshDatabase;

class EmergencyApiTest extends TestCase
{
    use RefreshDatabase;

    /**
     * Test can get active emergency alerts
     */
    public function test_can_get_active_alerts(): void
    {
        $response = $this->getJson('/api/v1/emergency/alerts/active');
        
        $response->assertStatus(200);
        $this->assertIsArray($response->json());
    }

    /**
     * Test can get emergency alert history
     */
    public function test_can_get_alert_history(): void
    {
        $response = $this->getJson('/api/v1/emergency/alerts/history');
        
        $response->assertStatus(200);
        $this->assertIsArray($response->json());
    }
}
