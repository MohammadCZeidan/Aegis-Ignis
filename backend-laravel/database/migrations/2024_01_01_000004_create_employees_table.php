<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('employees', function (Blueprint $table) {
            $table->id();
            $table->string('name');
            $table->string('employee_number')->unique()->nullable();
            $table->string('department')->nullable();
            $table->string('email')->unique()->nullable();
            $table->string('password');
            $table->string('role')->default('employee'); // admin, employee, security
            $table->string('status')->default('active'); // active, inactive, suspended
            $table->foreignId('floor_id')->nullable()->constrained()->onDelete('set null');
            $table->foreignId('current_floor_id')->nullable()->constrained('floors')->onDelete('set null');
            $table->string('current_room')->nullable();
            $table->json('face_embedding')->nullable();
            $table->text('face_photo_path')->nullable();
            $table->timestamp('face_registered_at')->nullable();
            $table->decimal('face_match_confidence', 5, 2)->nullable();
            $table->text('photo_url')->nullable();
            $table->timestamp('last_seen_at')->nullable();
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('employees');
    }
};

