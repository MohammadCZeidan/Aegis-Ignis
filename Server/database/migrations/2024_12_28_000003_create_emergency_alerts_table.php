<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('emergency_alerts', function (Blueprint $table) {
            $table->id();
            $table->enum('alert_type', ['fire_smoke', 'fire_small', 'fire_large', 'evacuation'])->default('fire_smoke');
            $table->enum('severity', ['warning', 'alert', 'critical'])->default('warning');
            $table->unsignedBigInteger('floor_id')->nullable();
            $table->string('room_location')->nullable();
            $table->string('camera_id')->nullable();
            $table->text('description');
            $table->string('detection_image_path')->nullable();
            $table->decimal('confidence', 5, 2);
            $table->integer('people_count')->default(0); // People in affected area
            $table->json('affected_employees')->nullable(); // Array of employee IDs
            $table->timestamp('detected_at');
            $table->timestamp('acknowledged_at')->nullable();
            $table->timestamp('resolved_at')->nullable();
            $table->boolean('police_notified')->default(false);
            $table->timestamp('police_notified_at')->nullable();
            $table->text('ai_message')->nullable(); // AI-generated alert message
            $table->enum('status', ['active', 'acknowledged', 'resolved', 'false_alarm'])->default('active');
            $table->timestamps();
            
            $table->foreign('floor_id')->references('id')->on('floors')->onDelete('set null');
            
            // Indexes
            $table->index(['status', 'severity', 'detected_at']);
            $table->index('floor_id');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('emergency_alerts');
    }
};
