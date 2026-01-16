<?php

namespace App\Services;

use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Storage;

class BuildingService
{
    public function getConfig(): object
    {
        $building = DB::table('buildings')->first();
        
        if (!$building) {
            $building = $this->createDefaultBuilding();
        }
        
        return $building;
    }
    
    public function updateConfig(array $data): object
    {
        $building = DB::table('buildings')->first();
        
        if (!$building) {
            return $this->createBuilding($data);
        }
        
        return $this->updateBuilding($building->id, $data);
    }
    
    public function deleteAllAlerts(): int
    {
        $deletedCount = 0;
        
        if (DB::getSchemaBuilder()->hasTable('fire_events')) {
            $deletedCount += DB::table('fire_events')->delete();
        }
        
        if (DB::getSchemaBuilder()->hasTable('fire_alerts')) {
            $deletedCount += DB::table('fire_alerts')->delete();
        }
        
        if (DB::getSchemaBuilder()->hasTable('alerts')) {
            $deletedCount += DB::table('alerts')
                ->where('event_type', 'fire_detection')
                ->delete();
        }
        
        $this->clearAlertImages();
        
        return $deletedCount;
    }
    
    private function createDefaultBuilding(): object
    {
        $id = DB::table('buildings')->insertGetId([
            'name' => 'Aegis Building',
            'total_floors' => 3,
            'created_at' => now(),
            'updated_at' => now(),
        ]);
        
        return DB::table('buildings')->find($id);
    }
    
    private function createBuilding(array $data): object
    {
        $id = DB::table('buildings')->insertGetId([
            'name' => $data['name'],
            'total_floors' => $data['total_floors'],
            'created_at' => now(),
            'updated_at' => now(),
        ]);
        
        return DB::table('buildings')->find($id);
    }
    
    private function updateBuilding(int $id, array $data): object
    {
        DB::table('buildings')
            ->where('id', $id)
            ->update([
                'name' => $data['name'],
                'total_floors' => $data['total_floors'],
                'updated_at' => now(),
            ]);
        
        return DB::table('buildings')->find($id);
    }
    
    private function clearAlertImages(): void
    {
        $alertsPath = storage_path('app/public/alerts');
        
        if (!is_dir($alertsPath)) {
            return;
        }
        
        $files = glob($alertsPath . '/*');
        foreach ($files as $file) {
            if (is_file($file)) {
                unlink($file);
            }
        }
    }
}
