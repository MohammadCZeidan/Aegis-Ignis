<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('fire_events', function (Blueprint $table) {
            if (!Schema::hasColumn('fire_events', 'room_location')) {
                $table->string('room_location')->nullable()->after('coordinates');
            }
        });
    }

    public function down(): void
    {
        Schema::table('fire_events', function (Blueprint $table) {
            $table->dropColumn('room_location');
        });
    }
};

