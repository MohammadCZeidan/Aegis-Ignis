<?php

namespace Tests\Feature\Api;

use Tests\TestCase;
use Illuminate\Foundation\Testing\RefreshDatabase;

class CameraApiTest extends TestCase
{
    use RefreshDatabase;

    /**
     * Test cameras index endpoint
     */
    public function test_can_get_cameras_list(): void
    {
        $response = $this->getJson('/api/v1/cameras');
        
        $response->assertStatus(200);
        $response->assertJsonStructure([
            'data'
        ]);
    }
}
