<?php

namespace App\Http\Middleware;

use Illuminate\Foundation\Http\Middleware\VerifyCsrfToken as Middleware;
class VerifyCsrfToken extends Middleware
{
    protected $except = [
        'api/*',
        '/api/*',
        'api/v1/*',
        '/api/v1/*',
    ];
}

