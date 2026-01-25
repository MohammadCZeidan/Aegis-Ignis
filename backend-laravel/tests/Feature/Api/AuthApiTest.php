<?php

namespace Tests\Feature\Api;

use Tests\TestCase;
use Illuminate\Foundation\Testing\RefreshDatabase;
use App\Models\User;

class AuthApiTest extends TestCase
{
    use RefreshDatabase;

    public function test_user_can_login(): void
    {
        $user = User::factory()->create([
            'email' => 'test@example.com',
            'password_hash' => bcrypt('password123')
        ]);

        $response = $this->postJson('/api/v1/auth/login/json', [
            'email' => 'test@example.com',
            'password' => 'password123'
        ]);

        $response->assertStatus(200);
        $response->assertJsonStructure(['access_token', 'token_type', 'user']);
    }

    public function test_login_fails_with_wrong_password(): void
    {
        $user = User::factory()->create([
            'email' => 'test@example.com',
            'password_hash' => bcrypt('password123')
        ]);

        $response = $this->postJson('/api/v1/auth/login/json', [
            'email' => 'test@example.com',
            'password' => 'wrongpassword'
        ]);

        $response->assertStatus(422);
    }

    public function test_login_fails_with_nonexistent_email(): void
    {
        $response = $this->postJson('/api/v1/auth/login/json', [
            'email' => 'nonexistent@example.com',
            'password' => 'password123'
        ]);

        $response->assertStatus(422);
    }

    public function test_login_requires_email(): void
    {
        $response = $this->postJson('/api/v1/auth/login/json', [
            'password' => 'password123'
        ]);

        $response->assertStatus(422);
        $response->assertJsonValidationErrors(['email']);
    }

    public function test_login_requires_password(): void
    {
        $response = $this->postJson('/api/v1/auth/login/json', [
            'email' => 'test@example.com'
        ]);

        $response->assertStatus(422);
        $response->assertJsonValidationErrors(['password']);
    }

    public function test_login_requires_valid_email_format(): void
    {
        $response = $this->postJson('/api/v1/auth/login/json', [
            'email' => 'invalid-email',
            'password' => 'password123'
        ]);

        $response->assertStatus(422);
        $response->assertJsonValidationErrors(['email']);
    }

    public function test_user_can_register(): void
    {
        $response = $this->postJson('/api/v1/auth/register', [
            'full_name' => 'New User',
            'email' => 'newuser@example.com',
            'password' => 'password123',
            'password_confirmation' => 'password123'
        ]);

        $response->assertStatus(201);
        $this->assertDatabaseHas('users', ['email' => 'newuser@example.com']);
    }

    public function test_register_requires_full_name(): void
    {
        $response = $this->postJson('/api/v1/auth/register', [
            'email' => 'newuser@example.com',
            'password' => 'password123',
            'password_confirmation' => 'password123'
        ]);

        $response->assertStatus(422);
        $response->assertJsonValidationErrors(['full_name']);
    }

    public function test_register_requires_email(): void
    {
        $response = $this->postJson('/api/v1/auth/register', [
            'full_name' => 'New User',
            'password' => 'password123',
            'password_confirmation' => 'password123'
        ]);

        $response->assertStatus(422);
        $response->assertJsonValidationErrors(['email']);
    }

    public function test_register_requires_password(): void
    {
        $response = $this->postJson('/api/v1/auth/register', [
            'full_name' => 'New User',
            'email' => 'newuser@example.com'
        ]);

        $response->assertStatus(422);
        $response->assertJsonValidationErrors(['password']);
    }

    public function test_register_requires_unique_email(): void
    {
        User::factory()->create(['email' => 'existing@example.com']);

        $response = $this->postJson('/api/v1/auth/register', [
            'full_name' => 'New User',
            'email' => 'existing@example.com',
            'password' => 'password123',
            'password_confirmation' => 'password123'
        ]);

        $response->assertStatus(422);
        $response->assertJsonValidationErrors(['email']);
    }

    public function test_register_requires_password_min_length(): void
    {
        $response = $this->postJson('/api/v1/auth/register', [
            'full_name' => 'New User',
            'email' => 'newuser@example.com',
            'password' => '12345',
            'password_confirmation' => '12345'
        ]);

        $response->assertStatus(422);
        $response->assertJsonValidationErrors(['password']);
    }

    public function test_register_accepts_valid_role(): void
    {
        $response = $this->postJson('/api/v1/auth/register', [
            'full_name' => 'New User',
            'email' => 'newuser@example.com',
            'password' => 'password123',
            'password_confirmation' => 'password123',
            'role' => 'admin'
        ]);

        $response->assertStatus(201);
    }

    public function test_login_fails_for_inactive_user(): void
    {
        $user = User::factory()->create([
            'email' => 'test@example.com',
            'password_hash' => bcrypt('password123'),
            'is_active' => false
        ]);

        $response = $this->postJson('/api/v1/auth/login/json', [
            'email' => 'test@example.com',
            'password' => 'password123'
        ]);

        $response->assertStatus(422);
    }
}
