<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use App\Models\User;
use Illuminate\Support\Facades\Hash;

class BasicUsersSeeder extends Seeder
{
    /**
     * Run the database seeds.
     * Only seeds Admin and HR users - everything else should be created through the UI
     */
    public function run(): void
    {
        // Create Admin User
        User::firstOrCreate(
            ['email' => 'admin@aegis-ignis.com'],
            [
                'name' => 'System Administrator',
                'password' => Hash::make('admin123'),
                'role' => 'admin',
                'is_active' => true,
            ]
        );

        echo "✓ Admin user created (admin@aegis-ignis.com / admin123)\n";

        // Create HR User
        User::firstOrCreate(
            ['email' => 'hr@aegis-ignis.com'],
            [
                'name' => 'HR Manager',
                'password' => Hash::make('hr123'),
                'role' => 'hr',
                'is_active' => true,
            ]
        );

        echo "✓ HR user created (hr@aegis-ignis.com / hr123)\n";

        echo "\n";
        echo "========================================\n";
        echo "  BASIC USERS SEEDED SUCCESSFULLY\n";
        echo "========================================\n";
        echo "Admin: admin@aegis-ignis.com / admin123\n";
        echo "HR:    hr@aegis-ignis.com / hr123\n";
        echo "\n";
        echo "All other data (floors, cameras, employees) should be\n";
        echo "created through the dashboard or registration system.\n";
        echo "========================================\n";
    }
}
