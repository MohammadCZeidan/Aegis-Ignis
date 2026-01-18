"""
Unused Employee Photos Cleanup Script

Identifies and removes employee photo files that are not referenced in the database.
Works with MySQL database and Laravel storage structure for employee management.

Usage:
    python cleanup_unused_photos.py [--dry-run] [--force]

Options:
    --dry-run    Show what would be deleted without actually deleting
    --force      Skip confirmation prompt
"""

import os
import sys
import mysql.connector
from pathlib import Path
from datetime import datetime
import argparse
from typing import Set, List, Dict, Any

class DatabaseConfig:
    """Database connection configuration"""
    
    HOST = '127.0.0.1'
    PORT = 3306
    USER = 'root'
    PASSWORD = ''
    DATABASE = 'aegis_ignis'
    
    @classmethod
    def get_config_dict(cls) -> Dict[str, Any]:
        return {
            'host': cls.HOST,
            'port': cls.PORT,
            'user': cls.USER,
            'password': cls.PASSWORD,
            'database': cls.DATABASE
        }

class FileSystemUtils:
    """Utility functions for file system operations"""
    
    @staticmethod
    def format_size(bytes_size: int) -> str:
        """Format bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.2f} TB"


def get_referenced_photos():
    """Get all photo paths referenced in the database"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        query = """
            SELECT face_photo_path, photo_url 
            FROM employees 
            WHERE face_photo_path IS NOT NULL OR photo_url IS NOT NULL
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        used_paths = set()
        for row in results:
            face_photo, photo_url = row
            if face_photo:
                used_paths.add(face_photo)
            if photo_url:
                # Extract path from URL
                path = photo_url.replace('/storage/', '').replace('storage/', '')
                used_paths.add(path)
        
        cursor.close()
        conn.close()
        
        return used_paths
        
    except mysql.connector.Error as err:
        print(f"❌ Database error: {err}")
        sys.exit(1)


def scan_directory(directory, used_paths):
    """Scan a directory for unused files"""
    dir_path = STORAGE_PATH / directory
    
    if not dir_path.exists():
        return []
    
    unused_files = []
    
    for file_path in dir_path.iterdir():
        if not file_path.is_file():
            continue
        
        # Check various path formats
        relative_path = f"{directory}/{file_path.name}"
        
        is_used = (
            relative_path in used_paths or
            f"public/{relative_path}" in used_paths or
            file_path.name in used_paths
        )
        
        if not is_used:
            stat = file_path.stat()
            unused_files.append({
                'path': file_path,
                'relative_path': relative_path,
                'size': stat.st_size,
                'modified': stat.st_mtime
            })
    
    return unused_files


def main():
    parser = argparse.ArgumentParser(
        description='Cleanup unused employee photos from storage'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be deleted without actually deleting'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Skip confirmation prompt'
    )
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("   UNUSED PHOTOS CLEANUP UTILITY")
    print("=" * 50)
    print()
    
    if args.dry_run:
        print("⚠️  DRY RUN MODE - No files will be deleted\n")
    
    # Get referenced photos from database
    print("📊 Scanning database for referenced photos...")
    used_paths = get_referenced_photos()
    print(f"   Found {len(used_paths)} photos referenced in database\n")
    
    # Scan directories
    all_unused_files = []
    total_files = 0
    
    for directory in DIRECTORIES:
        print(f"📁 Scanning directory: storage/app/public/{directory}")
        
        dir_path = STORAGE_PATH / directory
        if not dir_path.exists():
            print(f"   ⚠️  Directory does not exist, skipping...\n")
            continue
        
        unused_files = scan_directory(directory, used_paths)
        all_unused_files.extend(unused_files)
        
        files_count = len(list(dir_path.glob('*')))
        total_files += files_count
        
        print(f"   Files found: {files_count}")
        print(f"   Unused files: {len(unused_files)}\n")
    
    # Display results
    print("=" * 50)
    print("   SCAN RESULTS")
    print("=" * 50)
    print(f"Total files scanned:  {total_files}")
    print(f"Files in use:         {total_files - len(all_unused_files)}")
    print(f"Unused files:         {len(all_unused_files)}")
    print("-" * 50)
    print()
    
    if not all_unused_files:
        print("✅ No unused files found! Your storage is clean.")
        return
    
    # Display unused files
    print("📋 UNUSED FILES TO BE DELETED:\n")
    total_size = 0
    
    for file_info in all_unused_files:
        date_str = datetime.fromtimestamp(file_info['modified']).strftime('%Y-%m-%d %H:%M:%S')
        size_str = format_size(file_info['size'])
        print(f"   • {file_info['relative_path']}")
        print(f"     Size: {size_str} | Last modified: {date_str}")
        total_size += file_info['size']
    
    print(f"\n💾 Total space to be freed: {format_size(total_size)}\n")
    
    # Delete files
    if not args.dry_run:
        if not args.force:
            print(f"⚠️  WARNING: This will permanently delete {len(all_unused_files)} files!")
            confirmation = input("Do you want to proceed? (yes/no): ")
            
            if confirmation.lower() != 'yes':
                print("\n❌ Operation cancelled.")
                return
        
        print("\n🗑️  Deleting files...\n")
        
        deleted_count = 0
        error_count = 0
        
        for file_info in all_unused_files:
            try:
                file_info['path'].unlink()
                deleted_count += 1
                print(f"   ✓ Deleted: {file_info['relative_path']}")
            except Exception as e:
                error_count += 1
                print(f"   ✗ Error deleting {file_info['relative_path']}: {e}")
        
        print("\n" + "=" * 50)
        print("   CLEANUP COMPLETE")
        print("=" * 50)
        print(f"Files deleted:        {deleted_count}")
        print(f"Errors:               {error_count}")
        print(f"Space freed:          {format_size(total_size)}")
        print("=" * 50)
        
        if error_count == 0:
            print("\n✅ All unused photos have been successfully deleted!")
        else:
            print(f"\n⚠️  Cleanup completed with {error_count} errors.")
    else:
        print("\n✅ Dry run complete. No files were deleted.")
        print("   Run without --dry-run to actually delete files.")


if __name__ == '__main__':
    main()
