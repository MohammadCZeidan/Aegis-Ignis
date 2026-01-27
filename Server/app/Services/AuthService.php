<?php

namespace App\Services;

use App\Models\User;
use Illuminate\Support\Facades\Hash;

class AuthService
{
    /**
     * Create a new user
     */
    public function register(array $data): User
    {
        return User::create([
            'email' => $data['email'],
            'password_hash' => Hash::make($data['password']),
            'full_name' => $data['full_name'],
            'role' => $data['role'] ?? 'user',
            'is_active' => true,
        ]);
    }

    /**
     * Update user's last login timestamp
     */
    public function updateLastLogin(User $user): void
    {
        $user->update(['last_login' => now()]);
    }

    /**
     * Create authentication token for user
     */
    public function createToken(User $user): string
    {
        return $user->createToken('auth-token')->plainTextToken;
    }

    /**
     * Format user data for response
     */
    public function formatUserResponse(User $user): array
    {
        return [
            'id' => $user->id,
            'email' => $user->email,
            'full_name' => $user->full_name,
            'role' => $user->role,
            'is_active' => $user->is_active,
        ];
    }
}

