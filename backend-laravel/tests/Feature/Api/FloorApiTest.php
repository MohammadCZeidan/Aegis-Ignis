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
        $response->assertJsonStructure([
            'data' => [
                '*' => [
                    'id',
                    'name',
                    'floor_number'
                ]
            ]
        ]);
    }
}
