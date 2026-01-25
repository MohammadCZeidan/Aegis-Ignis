<?php

namespace Database\Factories;

use App\Models\Alert;
use App\Models\Camera;
use App\Models\Floor;
use Illuminate\Database\Eloquent\Factories\Factory;

class AlertFactory extends Factory
{
    protected $model = Alert::class;

    public function definition(): array
    {
        return [
            'event_type' => 'fire',
            'camera_id' => Camera::factory(),
            'floor_id' => Floor::factory(),
            'severity' => fake()->randomElement(['low', 'medium', 'high', 'critical']),
            'status' => fake()->randomElement(['active', 'acknowledged', 'resolved']),
            'confidence' => fake()->randomFloat(2, 0.5, 1.0),
            'detected_at' => now(),
        ];
    }

    /**
     * Ensure floor_id matches camera's floor_id after creation
     */
    public function configure(): static
    {
        return $this->afterCreating(function (Alert $alert) {
            if ($alert->camera && $alert->camera->floor_id && $alert->floor_id !== $alert->camera->floor_id) {
                $alert->update(['floor_id' => $alert->camera->floor_id]);
            }
        });
    }
}
