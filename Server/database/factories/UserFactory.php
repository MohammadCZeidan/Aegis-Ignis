<?php

namespace Database\Factories;

use App\Models\User;
use Illuminate\Database\Eloquent\Factories\Factory;
use Illuminate\Support\Facades\Hash;

class UserFactory extends Factory
{
    protected $model = User::class;

    public function definition(): array
    {
        return [
            'email' => fake()->unique()->safeEmail(),
            'password_hash' => Hash::make('password'),
            'full_name' => fake()->name(),
            'role' => fake()->randomElement(['user', 'admin', 'operator']),
            'is_active' => true,
        ];
    }
}
