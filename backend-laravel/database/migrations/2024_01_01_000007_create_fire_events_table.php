<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('fire_events', function (Blueprint $table) {
            $table->id();
            $table->foreignId('floor_id')->constrained()->onDelete('cascade');
            $table->foreignId('camera_id')->constrained()->onDelete('cascade');
            $table->string('detection_type'); // fire, smoke
            $table->float('confidence');
            $table->json('bounding_box')->nullable();
            $table->json('coordinates')->nullable();
            $table->string('room_location')->nullable(); // Room name or location where fire started
            $table->timestamp('timestamp')->useCurrent();
            $table->boolean('is_resolved')->default(false);
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('fire_events');
    }
};

