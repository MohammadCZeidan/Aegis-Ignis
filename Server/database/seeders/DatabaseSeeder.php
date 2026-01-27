<?php

namespace Database\Seeders;

use App\Models\User;
use App\Models\Building;
use App\Models\Floor;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\Hash;

class DatabaseSeeder extends Seeder
{
    public function run(): void
    {
        // Create admin user
        User::create([
            'email' => 'admin@aegis-ignis.com',
            'password_hash' => Hash::make('admin123'),
            'full_name' => 'System Administrator',
            'role' => 'admin',
            'is_active' => true,
        ]);

        // Create test user
        User::create([
            'email' => 'user@aegis-ignis.com',
            'password_hash' => Hash::make('user123'),
            'full_name' => 'Test User',
            'role' => 'user',
            'is_active' => true,
        ]);

        // Create building and floors
        $building = Building::create([
            'name' => 'Main Building',
            'address' => '123 Security Street, Tech City',
        ]);

        Floor::create([
            'building_id' => $building->id,
            'floor_number' => 1,
            'name' => 'Ground Floor',
        ]);

        Floor::create([
            'building_id' => $building->id,
            'floor_number' => 2,
            'name' => 'Second Floor',
        ]);

        Floor::create([
            'building_id' => $building->id,
            'floor_number' => 3,
            'name' => 'Third Floor',
        ]);

        $this->command->info('Database seeded successfully!');
        $this->command->info('Admin: admin@aegis-ignis.com / admin123');
        $this->command->info('User: user@aegis-ignis.com / user123');
    }
}

