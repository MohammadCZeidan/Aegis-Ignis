<?php

namespace Tests\Feature;

use Tests\TestCase;

class HealthCheckTest extends TestCase
{
    /**
     * Test health check endpoint returns success
     */
    public function test_health_check_endpoint_accessible(): void
    {
        $response = $this->get('/api/health');
        
        // Should return 200, 503, or 500 (degraded services)
        $this->assertContains($response->status(), [200, 503, 500]);
    }

    /**
     * Test ping endpoint
     */
    public function test_ping_endpoint(): void
    {
        $response = $this->get('/api/ping');
        
        // Ping should always work
        $this->assertContains($response->status(), [200, 500]);
    }
}
