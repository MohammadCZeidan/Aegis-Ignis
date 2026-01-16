<?php

namespace Database\Seeders;

use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;
use App\Models\Camera;
use App\Models\Floor;

class CameraSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        // Get floors by their floor_number
        $floors = Floor::all()->keyBy('floor_number');

        $cameras = [
            // Ground Floor (floor_number = 0)
            ['floor_id' => $floors[0]->id ?? 1, 'name' => 'Camera G-01 (Main Entrance)', 'rtsp_url' => 'rtsp://localhost:8554/stream0'],
            ['floor_id' => $floors[0]->id ?? 1, 'name' => 'Camera G-02 (Reception)', 'rtsp_url' => 'rtsp://localhost:8554/stream1'],
            ['floor_id' => $floors[0]->id ?? 1, 'name' => 'Camera G-03 (Lobby)', 'rtsp_url' => 'rtsp://localhost:8554/stream2'],
            // First Floor (floor_number = 1)
            ['floor_id' => $floors[1]->id ?? 2, 'name' => 'Camera 1-01 (Hallway)', 'rtsp_url' => 'rtsp://localhost:8554/stream3'],
            ['floor_id' => $floors[1]->id ?? 2, 'name' => 'Camera 1-02 (Conference)', 'rtsp_url' => 'rtsp://localhost:8554/stream4'],
            // Second Floor (floor_number = 2)
            ['floor_id' => $floors[2]->id ?? 3, 'name' => 'Camera 2-01 (Lab)', 'rtsp_url' => 'rtsp://localhost:8554/stream5'],
            ['floor_id' => $floors[2]->id ?? 3, 'name' => 'Camera 2-02 (Dev Area)', 'rtsp_url' => 'rtsp://localhost:8554/stream6'],
            // Third Floor (floor_number = 3)
            ['floor_id' => $floors[3]->id ?? 4, 'name' => 'Camera 3-01 (Executive)', 'rtsp_url' => 'rtsp://localhost:8554/stream7'],
            // Basement (floor_number = -1)
            ['floor_id' => $floors[-1]->id ?? 5, 'name' => 'Camera B1-01 (Server)', 'rtsp_url' => 'rtsp://localhost:8554/stream8'],
            ['floor_id' => $floors[-1]->id ?? 5, 'name' => 'Camera B1-02 (Parking)', 'rtsp_url' => 'rtsp://localhost:8554/stream9'],
        ];

        foreach ($cameras as $camera) {
            Camera::firstOrCreate(
                ['name' => $camera['name']],
                $camera
            );
        }
    }
}
