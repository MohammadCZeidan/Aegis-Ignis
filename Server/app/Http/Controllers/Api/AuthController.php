<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\LoginRequest;
use App\Http\Requests\RegisterRequest;
use App\Services\AuthService;
use Illuminate\Http\Request;

class AuthController extends Controller
{
    protected AuthService $authService;
    public function __construct(AuthService $authService)
    {
        $this->authService = $authService;
    }

    /**
     * Login endpoint (JSON format)
     */
    public function login(LoginRequest $request)
    {
        $user = $request->authenticate();
        $this->authService->updateLastLogin($user);
        $token = $this->authService->createToken($user);

        return response()->json([
            'access_token' => $token,
            'token_type' => 'bearer',
            'user' => $this->authService->formatUserResponse($user),
        ]);
    }

    /**
     * Register a new user
     */
    public function register(RegisterRequest $request)
    {
        $user = $this->authService->register($request->validated());

        return response()->json($this->authService->formatUserResponse($user), 201);
    }

    /**
     * Get current authenticated user
     */
    public function me(Request $request)
    {
        $user = $request->user();
        
        if (!$user) {
            return response()->json([
                'message' => 'Unauthenticated'
            ], 401);
        }
        
        return response()->json($this->authService->formatUserResponse($user));
    }
}

