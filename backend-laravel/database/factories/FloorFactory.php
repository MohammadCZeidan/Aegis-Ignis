<?php

namespace Database\Factories;

use App\Models\Floor;
use App\Models\Building;
use Illuminate\Database\Eloquent\Factories\Factory;

class FloorFactory extends Factory
{
    protected $model = Floor::class;

    public function definition(): array
    {
        return [
            'building_id' => Building::factory(),
            'floor_number' => fake()->numberBetween(0, 10),
            'name' => fake()->randomElement(['Ground Floor', 'First Floor', 'Second Floor', 'Third Floor', 'Basement']),
        ];
    }
}
