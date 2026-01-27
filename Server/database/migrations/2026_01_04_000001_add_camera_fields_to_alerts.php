<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('alerts', function (Blueprint $table) {
            $table->string('camera_id')->nullable()->after('floor_id');
            $table->string('camera_name')->nullable()->after('camera_id');
            $table->string('room')->nullable()->after('camera_name');
            $table->float('confidence')->nullable()->after('severity');
            $table->string('fire_type')->nullable()->after('confidence');
            $table->text('screenshot_path')->nullable()->after('fire_type');
            $table->timestamp('detected_at')->nullable()->after('screenshot_path');
        });
    }

    public function down(): void
    {
        Schema::table('alerts', function (Blueprint $table) {
            $table->dropColumn([
                'camera_id',
                'camera_name',
                'room',
                'confidence',
                'fire_type',
                'screenshot_path',
                'detected_at'
            ]);
        });
    }
};
