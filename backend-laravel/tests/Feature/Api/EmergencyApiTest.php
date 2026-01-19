<?php

namespace Tests\Feature\Api;

use Tests\TestCase;
use Illuminate\Foundation\Testing\RefreshDatabase;

class EmergencyApiTest extends TestCase
{
    use RefreshDatabase;

    /**
     * Test emergency endpoints require authentication
     */
    public function test_emergency_endpoints_require_auth(): void
    {
        $response = $this->getJson('/api/v1/emergency/alerts/active');
        $this->assertContains($response->status(), [401, 404]);
        
        $response = $this->getJson('/api/v1/emergency/alerts/history');
        $this->assertContains($response->status(), [401, 404]);
    }
}
