<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        if (!Schema::hasColumn('buildings', 'total_floors')) {
            Schema::table('buildings', function (Blueprint $table) {
                $table->integer('total_floors')->default(3)->after('name');
            });
        }
    }

    public function down(): void
    {
        if (Schema::hasColumn('buildings', 'total_floors')) {
            Schema::table('buildings', function (Blueprint $table) {
                $table->dropColumn('total_floors');
            });
        }
    }
};
