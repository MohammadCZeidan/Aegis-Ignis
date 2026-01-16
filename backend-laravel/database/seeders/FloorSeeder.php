<?php

namespace Database\Seeders;

use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;
use App\Models\Floor;

class FloorSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        // First ensure there's a building - use building_id = 1
        $floors = [
            ['building_id' => 1, 'name' => 'Ground Floor', 'floor_number' => 0],
            ['building_id' => 1, 'name' => 'First Floor', 'floor_number' => 1],
            ['building_id' => 1, 'name' => 'Second Floor', 'floor_number' => 2],
            ['building_id' => 1, 'name' => 'Third Floor', 'floor_number' => 3],
            ['building_id' => 1, 'name' => 'Basement', 'floor_number' => -1],
        ];

        foreach ($floors as $floor) {
            Floor::firstOrCreate(
                ['floor_number' => $floor['floor_number'], 'building_id' => $floor['building_id']],
                $floor
            );
        }
    }
}
