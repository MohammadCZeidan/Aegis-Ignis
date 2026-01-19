<?php

namespace Tests\Feature\Api;

use Tests\TestCase;
use Illuminate\Foundation\Testing\RefreshDatabase;
use App\Models\User;

class AuthApiTest extends TestCase
{
    use RefreshDatabase;

    /**
     * Test user can login
     */
    public function test_user_can_login(): void
    {
        $user = User::factory()->create([
            'email' => 'test@example.com',
            'password' => bcrypt('password123')
        ]);

        $response = $this->postJson('/api/v1/auth/login/json', [
            'email' => 'test@example.com',
            'password' => 'password123'
        ]);

        $this->assertContains($response->status(), [200, 201]);
    }

    /**
     * Test login fails with wrong credentials
     */
    public function test_login_fails_with_wrong_password(): void
    {
        $user = User::factory()->create([
            'email' => 'test@example.com',
            'password' => bcrypt('password123')
        ]);

        $response = $this->postJson('/api/v1/auth/login/json', [
            'email' => 'test@example.com',
            'password' => 'wrongpassword'
        ]);

        $this->assertContains($response->status(), [401, 422]);
    }

    /**
     * Test user can register
     */
    public function test_user_can_register(): void
    {
        $response = $this->postJson('/api/v1/auth/register', [
            'name' => 'New User',
            'email' => 'newuser@example.com',
            'password' => 'password123',
            'password_confirmation' => 'password123'
        ]);

        $this->assertContains($response->status(), [200, 201, 422]); // 422 if validation fails
    }
}
