<?php

namespace Database\Factories;

use App\Models\Floor;
use Illuminate\Database\Eloquent\Factories\Factory;

class FloorFactory extends Factory
{
    protected $model = Floor::class;

    public function definition(): array
    {
        return [
            'name' => fake()->randomElement(['Ground Floor', 'First Floor', 'Second Floor', 'Third Floor', 'Basement']),
            'floor_number' => fake()->numberBetween(0, 10),
            'description' => fake()->sentence(),
        ];
    }
}
