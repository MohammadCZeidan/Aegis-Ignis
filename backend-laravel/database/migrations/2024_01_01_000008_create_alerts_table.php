<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('alerts', function (Blueprint $table) {
            $table->id();
            $table->string('event_type'); // fire, smoke, security
            $table->foreignId('floor_id')->constrained()->onDelete('cascade');
            $table->foreignId('fire_event_id')->nullable()->constrained()->onDelete('set null');
            $table->string('severity'); // low, medium, high, critical
            $table->string('status')->default('active'); // active, acknowledged, resolved
            $table->timestamp('resolved_at')->nullable();
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('alerts');
    }
};

