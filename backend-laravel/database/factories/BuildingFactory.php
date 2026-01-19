<?php

namespace Database\Factories;

use App\Models\Building;
use Illuminate\Database\Eloquent\Factories\Factory;

class BuildingFactory extends Factory
{
    protected $model = Building::class;

    public function definition(): array
    {
        return [
            'name' => fake()->company() . ' Building',
            'address' => fake()->address(),
            'floors_count' => fake()->numberBetween(1, 10),
            'is_active' => true,
        ];
    }
}
