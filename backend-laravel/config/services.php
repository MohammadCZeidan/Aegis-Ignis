<?php

return [

    /*
    |--------------------------------------------------------------------------
    | Third Party Services
    |--------------------------------------------------------------------------
    */

    'postmark' => [
        'token' => env('POSTMARK_TOKEN'),
    ],

    'ses' => [
        'key' => env('AWS_ACCESS_KEY_ID'),
        'secret' => env('AWS_SECRET_ACCESS_KEY'),
        'region' => env('AWS_DEFAULT_REGION', 'us-east-1'),
    ],

    'resend' => [
        'key' => env('RESEND_KEY'),
    ],

    'slack' => [
        'notifications' => [
            'bot_user_oauth_token' => env('SLACK_BOT_USER_OAUTH_TOKEN'),
            'channel' => env('SLACK_BOT_USER_DEFAULT_CHANNEL'),
        ],
    ],

    /*
    |--------------------------------------------------------------------------
    | Microservices Configuration
    |--------------------------------------------------------------------------
    */

    'microservices' => [
        // Face Detection Service
        'face_service_url' => env('FACE_SERVICE_URL', 'http://localhost:8001'),
        
        // Fire Detection Service
        'fire_service_url' => env('FIRE_SERVICE_URL', 'http://localhost:8002'),
        
        // Request timeout in seconds
        'timeout' => env('MICROSERVICE_TIMEOUT', 10),
        
        // Maximum retry attempts
        'max_retries' => env('MICROSERVICE_MAX_RETRIES', 3),
        
        // Retry delay in milliseconds
        'retry_delay' => env('MICROSERVICE_RETRY_DELAY', 100),
        
        // Circuit breaker threshold (number of failures before opening circuit)
        'circuit_breaker_threshold' => env('MICROSERVICE_CIRCUIT_BREAKER_THRESHOLD', 5),
        
        // Circuit breaker TTL in seconds (how long to keep circuit open)
        'circuit_breaker_ttl' => env('MICROSERVICE_CIRCUIT_BREAKER_TTL', 60),
    ],

    /*
    |--------------------------------------------------------------------------
    | AWS S3 Configuration
    |--------------------------------------------------------------------------
    */

    's3' => [
        'key' => env('AWS_ACCESS_KEY_ID'),
        'secret' => env('AWS_SECRET_ACCESS_KEY'),
        'region' => env('AWS_DEFAULT_REGION', 'us-east-1'),
        'bucket' => env('AWS_BUCKET'),
    ],

    /*
    |--------------------------------------------------------------------------
    | Twilio Configuration
    |--------------------------------------------------------------------------
    */

    'twilio' => [
        'account_sid' => env('TWILIO_ACCOUNT_SID'),
        'auth_token' => env('TWILIO_AUTH_TOKEN'),
        'from_number' => env('TWILIO_FROM_NUMBER'),
    ],

];
