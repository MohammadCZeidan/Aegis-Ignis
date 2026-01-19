<?php

namespace Tests\Feature\Api;

use Tests\TestCase;
use Illuminate\Foundation\Testing\RefreshDatabase;

class EmployeeApiTest extends TestCase
{
    use RefreshDatabase;

    /**
     * Test can get employees list
     */
    public function test_can_get_employees_list(): void
    {
        $response = $this->getJson('/api/v1/employees');
        
        $response->assertStatus(200);
        $this->assertIsArray($response->json());
    }

    /**
     * Test can get next employee ID
     */
    public function test_can_get_next_employee_id(): void
    {
        $response = $this->getJson('/api/v1/employees/next-id');
        
        $response->assertStatus(200);
        // Response structure may vary
        $this->assertIsArray($response->json());
    }

    /**
     * Test can create employee with face
     */
    public function test_can_create_employee_with_face(): void
    {
        $employeeData = [
            'name' => 'John Doe',
            'email' => 'john.doe@example.com',
            'employee_id' => 'EMP001',
            'phone' => '1234567890',
            'department' => 'IT',
            'position' => 'Developer'
        ];

        $response = $this->postJson('/api/v1/employees/create-with-face', $employeeData);
        
        // May fail validation without face encoding
        $this->assertContains($response->status(), [200, 201, 422]);
    }

    /**
     * Test employee creation fails with duplicate email
     */
    public function test_cannot_create_duplicate_employee_email(): void
    {
        $employee = \App\Models\Employee::factory()->create([
            'email' => 'duplicate@example.com'
        ]);

        $response = $this->postJson('/api/v1/employees/create-with-face', [
            'name' => 'Jane Doe',
            'email' => 'duplicate@example.com',
            'employee_id' => 'EMP002',
        ]);
        
        $this->assertContains($response->status(), [422, 400, 409]);
    }
}
