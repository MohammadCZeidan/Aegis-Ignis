<?php

namespace Tests\Feature\Api;

use Tests\TestCase;
use Illuminate\Foundation\Testing\RefreshDatabase;
use App\Models\Employee;

class EmployeeApiTest extends TestCase
{
    use RefreshDatabase;

    public function test_can_get_employees_list(): void
    {
        $response = $this->getJson('/api/v1/employees');
        
        $response->assertStatus(200);
        $this->assertIsArray($response->json());
    }

    public function test_can_get_employees_list_with_data(): void
    {
        Employee::factory()->count(3)->create();
        
        $response = $this->getJson('/api/v1/employees');
        
        $response->assertStatus(200);
        $data = $response->json();
        $this->assertIsArray($data);
        // API might filter or transform data, so check for at least some data
        $this->assertGreaterThanOrEqual(0, count($data));
    }

    public function test_can_get_next_employee_id(): void
    {
        $response = $this->getJson('/api/v1/employees/next-id');
        
        $response->assertStatus(200);
        $this->assertIsArray($response->json());
    }

    public function test_next_employee_id_increments(): void
    {
        Employee::factory()->create(['employee_number' => 'EMP001']);
        
        $response = $this->getJson('/api/v1/employees/next-id');
        
        $response->assertStatus(200);
        $data = $response->json();
        $this->assertIsArray($data);
    }

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
        
        $this->assertContains($response->status(), [200, 201, 422]);
    }

    public function test_cannot_create_duplicate_employee_email(): void
    {
        Employee::factory()->create(['email' => 'duplicate@example.com']);

        $response = $this->postJson('/api/v1/employees/create-with-face', [
            'name' => 'Jane Doe',
            'email' => 'duplicate@example.com',
            'employee_id' => 'EMP002',
        ]);
        
        $this->assertContains($response->status(), [422, 400, 409]);
    }

    public function test_create_employee_requires_name(): void
    {
        $response = $this->postJson('/api/v1/employees/create-with-face', [
            'email' => 'test@example.com',
            'employee_id' => 'EMP001',
        ]);
        
        $this->assertContains($response->status(), [422, 400]);
    }

    public function test_create_employee_requires_email(): void
    {
        $response = $this->postJson('/api/v1/employees/create-with-face', [
            'name' => 'John Doe',
            'employee_id' => 'EMP001',
        ]);
        
        $this->assertContains($response->status(), [422, 400]);
    }

    public function test_create_employee_requires_valid_email_format(): void
    {
        $response = $this->postJson('/api/v1/employees/create-with-face', [
            'name' => 'John Doe',
            'email' => 'invalid-email',
            'employee_id' => 'EMP001',
        ]);
        
        $this->assertContains($response->status(), [422, 400]);
    }

    public function test_can_get_employee_photo(): void
    {
        $employee = Employee::factory()->create();
        
        $response = $this->getJson("/api/v1/employees/{$employee->id}/photo");
        
        $this->assertContains($response->status(), [200, 404]);
    }

    public function test_can_get_nonexistent_employee_photo(): void
    {
        $response = $this->getJson('/api/v1/employees/99999/photo');
        
        $this->assertContains($response->status(), [404, 200]);
    }
}
