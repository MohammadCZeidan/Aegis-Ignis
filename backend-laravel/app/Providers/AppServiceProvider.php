<?php

namespace App\Providers;

use Illuminate\Support\ServiceProvider;
use App\Services\Gateway\FaceServiceClient;

class AppServiceProvider extends ServiceProvider
{
    public function register(): void
    {
        // Register Gateway Services as Singletons
        $this->app->singleton(FaceServiceClient::class, function ($app) {
            return new FaceServiceClient();
        });
    }

    public function boot(): void
    {
        // Boot application services
    }
}

