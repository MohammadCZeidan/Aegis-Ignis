<?php

namespace Database\Factories;

use App\Models\Camera;
use App\Models\Floor;
use Illuminate\Database\Eloquent\Factories\Factory;

class CameraFactory extends Factory
{
    protected $model = Camera::class;

    public function definition(): array
    {
        return [
            'floor_id' => Floor::factory(),
            'name' => fake()->words(3, true) . ' Camera',
            'rtsp_url' => 'rtsp://' . fake()->ipv4() . ':554/stream',
            'position_x' => fake()->randomFloat(2, 0, 100),
            'position_y' => fake()->randomFloat(2, 0, 100),
            'position_z' => fake()->randomFloat(2, 0, 10),
            'is_active' => fake()->boolean(80),
        ];
    }
}
