<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;

class SyncCameraConfigSeeder extends Seeder
{
    /**
     * Sync cameras from camera_config.json to database
     */
    public function run(): void
    {
        $configPath = base_path('../camera_config.json');
        
        if (!file_exists($configPath)) {
            $this->command->error("camera_config.json not found!");
            return;
        }
        
        $config = json_decode(file_get_contents($configPath), true);
        $cameras = $config['cameras'] ?? [];
        
        foreach ($cameras as $camera) {
            DB::table('cameras')->updateOrInsert(
                ['id' => $camera['id']],
                [
                    'name' => $camera['name'],
                    'rtsp_url' => $camera['stream_url'],
                    'floor_id' => $camera['floor_id'],
                    'room' => $camera['room'] ?? null,
                    'is_active' => $camera['is_active'] ?? true,
                    'created_at' => now(),
                    'updated_at' => now(),
                ]
            );
        }
        
        $this->command->info('✓ Synced ' . count($cameras) . ' cameras from camera_config.json to database');
    }
}
