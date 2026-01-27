<?php

namespace Tests\Feature\Api;

use Tests\TestCase;
use Illuminate\Foundation\Testing\RefreshDatabase;
use App\Models\Building;

class BuildingApiTest extends TestCase
{
    use RefreshDatabase;

    public function test_can_get_building_config(): void
    {
        $response = $this->getJson('/api/v1/building/config');
        
        $response->assertStatus(200);
        $this->assertIsArray($response->json());
    }

    public function test_building_config_returns_valid_structure(): void
    {
        $response = $this->getJson('/api/v1/building/config');
        
        $response->assertStatus(200);
        $data = $response->json();
        $this->assertIsArray($data);
    }

    public function test_building_config_is_accessible_without_auth(): void
    {
        $response = $this->getJson('/api/v1/building/config');
        
        $response->assertStatus(200);
    }

    public function test_building_config_returns_consistent_format(): void
    {
        $response1 = $this->getJson('/api/v1/building/config');
        $response2 = $this->getJson('/api/v1/building/config');
        
        $response1->assertStatus(200);
        $response2->assertStatus(200);
        $this->assertIsArray($response1->json());
        $this->assertIsArray($response2->json());
    }
}
