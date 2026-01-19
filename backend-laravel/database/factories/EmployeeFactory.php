<?php

namespace Database\Factories;

use App\Models\Employee;
use Illuminate\Database\Eloquent\Factories\Factory;

class EmployeeFactory extends Factory
{
    protected $model = Employee::class;

    public function definition(): array
    {
        return [
            'name' => fake()->name(),
            'email' => fake()->unique()->safeEmail(),
            'employee_id' => 'EMP-' . fake()->unique()->numberBetween(1000, 9999),
            'phone' => fake()->phoneNumber(),
            'department' => fake()->randomElement(['IT', 'HR', 'Finance', 'Operations', 'Sales']),
            'position' => fake()->randomElement(['Manager', 'Developer', 'Analyst', 'Coordinator', 'Specialist']),
            'status' => 'active',
        ];
    }
}
