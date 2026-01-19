<?php

namespace Tests\Feature;

use Tests\TestCase;
use Illuminate\Foundation\Testing\RefreshDatabase;

class HealthCheckTest extends TestCase
{
    /**
     * Test health check endpoint returns 200 or 503
     */
    public function test_health_check_endpoint_accessible(): void
    {
        $response = $this->get('/api/health');
        
        // Should return either 200 (healthy) or 503 (degraded)
        $this->assertContains($response->status(), [200, 503]);
        
        $response->assertJsonStructure([
            'status',
            'timestamp',
            'checks'
        ]);
    }

    /**
     * Test ping endpoint
     */
    public function test_ping_endpoint(): void
    {
        $response = $this->get('/api/ping');
        
        $response->assertStatus(200);
        $response->assertJson(['status' => 'ok']);
    }
}
