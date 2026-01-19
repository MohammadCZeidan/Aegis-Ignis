<?php

namespace Tests\Feature\Api;

use Tests\TestCase;
use Illuminate\Foundation\Testing\RefreshDatabase;

class BuildingApiTest extends TestCase
{
    use RefreshDatabase;

    /**
     * Test can get building config
     */
    public function test_can_get_building_config(): void
    {
        $response = $this->getJson('/api/v1/building/config');
        
        $response->assertStatus(200);
        $this->assertIsArray($response->json());
    }
}
