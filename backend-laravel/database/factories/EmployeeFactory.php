<?php

namespace Database\Factories;

use App\Models\Employee;
use Illuminate\Support\Facades\Hash;
use Illuminate\Database\Eloquent\Factories\Factory;

class EmployeeFactory extends Factory
{
    protected $model = Employee::class;

    public function definition(): array
    {
        return [
            'name' => fake()->name(),
            'employee_number' => 'EMP-' . fake()->unique()->numberBetween(1000, 9999),
            'department' => fake()->randomElement(['IT', 'HR', 'Finance', 'Operations', 'Sales']),
            'email' => fake()->unique()->safeEmail(),
            'password' => Hash::make('password'),
            'role' => fake()->randomElement(['employee', 'admin', 'security']),
            'status' => 'active',
        ];
    }
}
