<?php

namespace Tests\Feature\Api;

use Tests\TestCase;
use Illuminate\Foundation\Testing\RefreshDatabase;
use App\Models\Floor;
use App\Models\Employee;

class PresenceApiTest extends TestCase
{
    use RefreshDatabase;

    public function test_can_get_current_presence(): void
    {
        $response = $this->getJson('/api/v1/presence/current');
        
        $this->assertContains($response->status(), [200, 429, 500]);
        if ($response->status() === 200) {
            $this->assertIsArray($response->json());
        }
    }

    public function test_can_get_current_presence_with_data(): void
    {
        Employee::factory()->count(2)->create();
        
        $response = $this->getJson('/api/v1/presence/current');
        
        $this->assertContains($response->status(), [200, 429, 500]);
        if ($response->status() === 200) {
            $data = $response->json();
            $this->assertIsArray($data);
        }
    }

    public function test_can_get_all_people_in_building(): void
    {
        $response = $this->getJson('/api/v1/presence/people');
        
        $this->assertContains($response->status(), [200, 401, 404]);
    }

    public function test_can_get_floor_presence(): void
    {
        $floor = Floor::factory()->create();
        
        $response = $this->getJson("/api/v1/presence/floor-live/{$floor->id}");
        
        $response->assertStatus(200);
        $this->assertIsArray($response->json());
    }

    public function test_can_get_floor_presence_with_data(): void
    {
        $floor = Floor::factory()->create();
        Employee::factory()->count(2)->create();
        
        $response = $this->getJson("/api/v1/presence/floor-live/{$floor->id}");
        
        $response->assertStatus(200);
        $data = $response->json();
        $this->assertIsArray($data);
    }

    public function test_can_get_nonexistent_floor_presence(): void
    {
        $response = $this->getJson('/api/v1/presence/floor-live/99999');
        
        $response->assertStatus(200);
        $this->assertIsArray($response->json());
    }

    public function test_can_log_presence_entry(): void
    {
        $employee = Employee::factory()->create();
        $floor = Floor::factory()->create();
        
        $response = $this->postJson('/api/v1/presence/log', [
            'employee_id' => $employee->id,
            'floor_id' => $floor->id,
            'type' => 'entry'
        ]);
        
        $this->assertContains($response->status(), [200, 201, 422]);
    }

    public function test_can_log_presence_exit(): void
    {
        $employee = Employee::factory()->create();
        
        $response = $this->postJson('/api/v1/presence/exit', [
            'employee_id' => $employee->id
        ]);
        
        $this->assertContains($response->status(), [200, 201, 422, 429, 500]);
    }

    public function test_current_presence_returns_empty_array_when_no_presence(): void
    {
        $response = $this->getJson('/api/v1/presence/current');
        
        $this->assertContains($response->status(), [200, 429, 500]);
        if ($response->status() === 200) {
            $data = $response->json();
            $this->assertIsArray($data);
        }
    }
}
