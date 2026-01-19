<?php

namespace Database\Factories;

use App\Models\Camera;
use Illuminate\Database\Eloquent\Factories\Factory;

class CameraFactory extends Factory
{
    protected $model = Camera::class;

    public function definition(): array
    {
        return [
            'camera_id' => 'CAM-' . fake()->unique()->numberBetween(1000, 9999),
            'name' => fake()->words(3, true) . ' Camera',
            'location' => fake()->randomElement(['Entrance', 'Hallway', 'Lobby', 'Office', 'Stairwell']),
            'floor_id' => null,
            'ip_address' => fake()->localIpv4(),
            'status' => fake()->randomElement(['active', 'inactive', 'maintenance']),
            'stream_url' => 'rtsp://' . fake()->ipv4() . ':554/stream',
        ];
    }
}
