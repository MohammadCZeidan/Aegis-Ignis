<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;
use Illuminate\Support\Facades\DB;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::table('employees', function (Blueprint $table) {
            // Add a boolean column to track if face is registered for faster queries
            $table->boolean('has_face_embedding')->default(false)->after('face_embedding');
            $table->index('has_face_embedding'); // Add index
        });
        
        // Update existing records (use true for PostgreSQL boolean)
        DB::statement('UPDATE employees SET has_face_embedding = true WHERE face_embedding IS NOT NULL');
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('employees', function (Blueprint $table) {
            $table->dropIndex(['has_face_embedding']);
            $table->dropColumn('has_face_embedding');
        });
    }
};
