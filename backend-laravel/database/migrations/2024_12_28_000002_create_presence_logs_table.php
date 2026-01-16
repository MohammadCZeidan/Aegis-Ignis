<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('presence_logs', function (Blueprint $table) {
            $table->id();
            $table->unsignedBigInteger('employee_id');
            $table->unsignedBigInteger('floor_id')->nullable();
            $table->string('room_location')->nullable();
            $table->string('camera_id')->nullable();
            $table->decimal('confidence', 5, 2); // 0.00 to 100.00
            $table->string('detection_image_path')->nullable();
            $table->enum('event_type', ['entry', 'exit', 'movement', 'detected'])->default('detected');
            $table->timestamp('detected_at');
            $table->json('metadata')->nullable(); // Additional data like bbox, embeddings, etc.
            $table->timestamps();
            
            $table->foreign('employee_id')->references('id')->on('employees')->onDelete('cascade');
            $table->foreign('floor_id')->references('id')->on('floors')->onDelete('set null');
            
            // Index for faster queries
            $table->index(['employee_id', 'detected_at']);
            $table->index(['floor_id', 'detected_at']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('presence_logs');
    }
};
