"""
Fire Alert Images Cleanup Script

Identifies and removes fire detection alert images based on various criteria:
1. Images marked as false alarms in the database
2. Resolved/acknowledged alerts older than specified days
3. Images not referenced in active alerts

Usage:
    python cleanup_fire_alerts.py [--dry-run] [--days=7] [--include-resolved]

Options:
    --dry-run            Show what would be deleted without actually deleting
    --days=N             Keep alerts from last N days (default: 7)
    --include-resolved   Also delete images from resolved alerts
    --force              Skip confirmation prompt
"""

import os
import sys
import mysql.connector
from pathlib import Path
from datetime import datetime, timedelta
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


def get_images_to_keep(days_to_keep, include_resolved):
    """Get list of image paths that should be kept"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        # Build query based on options
        if not include_resolved:
            # Keep all images from active and acknowledged alerts
            query = """
                SELECT detection_image_path 
                FROM emergency_alerts 
                WHERE detection_image_path IS NOT NULL 
                  AND status IN ('active', 'acknowledged')
            """
            cursor.execute(query)
        elif days_to_keep > 0:
            # Only keep recent alerts (including resolved ones)
            query = """
                SELECT detection_image_path 
                FROM emergency_alerts 
                WHERE detection_image_path IS NOT NULL 
                  AND detected_at >= %s
            """
            cursor.execute(query, (cutoff_date,))
        else:
            # Keep active alerts only, delete everything else
            query = """
                SELECT detection_image_path 
                FROM emergency_alerts 
                WHERE detection_image_path IS NOT NULL 
                  AND status = 'active'
            """
            cursor.execute(query)
        
        results = cursor.fetchall()
        
        keep_paths = set()
        for row in results:
            if row[0]:
                # Remove 'alerts/' prefix if present
                path = row[0].replace('alerts/', '')
                keep_paths.add(path)
        
        cursor.close()
        conn.close()
        
        return keep_paths

class AlertImageAnalyzer(AlertImageDatabase):
    """Extends database operations to include analysis and breakdown functionality."""
    
    def get_alert_status_breakdown(self) -> Dict[str, Dict[str, int]]:
        """Get breakdown of alerts by status"""
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT status, COUNT(*) as count, 
                       COUNT(detection_image_path) as with_images
                FROM emergency_alerts
                GROUP BY status
            """)
            
            results = cursor.fetchall()
            breakdown = {}
            
            for status, count, with_images in results:
                breakdown[status] = {
                    'count': count,
                    'with_images': with_images
                }
            
            cursor.close()
            conn.close()
            
            return breakdown
            
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            sys.exit(1)

class ImageFileManager:
    """Handles file system operations for alert images."""
    
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
    
    def get_deletable_images(self, keep_paths: Set[str]) -> List[Dict]:
        """Scan alerts directory for images that can be deleted"""
        if not self.storage_path.exists():
            print(f"Alerts directory not found: {self.storage_path}")
            return []
        
        deletable_images = []
        
        for file_path in self.storage_path.iterdir():
            if not file_path.is_file():
                continue
            
            if file_path.name not in keep_paths:
                stat_info = file_path.stat()
                deletable_images.append({
                    'path': file_path,
                    'name': file_path.name,
                    'size': stat_info.st_size,
                    'modified': stat_info.st_mtime
                })
        
        return deletable_images
    
    def delete_images(self, deletable_images: List[Dict], dry_run: bool = False) -> int:
        """Delete the specified images from file system"""
        deleted_count = 0
        
        for image in deletable_images:
            try:
                if not dry_run:
                    image['path'].unlink()
                deleted_count += 1
                
            except Exception as e:
                print(f"Error deleting {image['name']}: {e}")
        
        return deleted_count

class FireAlertCleanupApp:
    """Main application class for fire alert image cleanup."""
    
    def __init__(self):
        self.storage_path = Path(__file__).parent / 'backend-laravel' / 'storage' / 'app' / 'public' / 'alerts'
        self.analyzer = AlertImageAnalyzer()
        self.file_manager = ImageFileManager(self.storage_path)
    
    def run(self, args):
        """Execute the cleanup process based on provided arguments."""
        try:
            self._display_header()
            self._show_current_status()
            
            keep_paths = self.analyzer.get_images_to_keep(args.days, args.include_resolved)
            deletable_images = self.file_manager.get_deletable_images(keep_paths)
            
            if not deletable_images:
                print("\nNo images to clean up!\n")
                return
            
            self._show_cleanup_summary(deletable_images, args)
            
            if not args.dry_run and not args.force:
                if not self._get_user_confirmation():
                    print("Cleanup cancelled.")
                    return
            
            self._perform_cleanup(deletable_images, args.dry_run)
            
        except KeyboardInterrupt:
            print("\nCleanup cancelled by user.")
        except Exception as e:
            print(f"Unexpected error: {e}")
            sys.exit(1)
    
    def _display_header(self):
        """Display application header."""
        print("=" * 50)
        print("    FIRE ALERT IMAGE CLEANUP")
        print("=" * 50)
        print()
    
    def _show_current_status(self):
        """Display current database and file system status."""
        print("Current Status:")
        breakdown = self.analyzer.get_alert_status_breakdown()
        
        for status, data in breakdown.items():
            print(f"  {status.title()}: {data['count']} alerts ({data['with_images']} with images)")
        
        total_files = len(list(self.storage_path.glob('*.*'))) if self.storage_path.exists() else 0
        print(f"  Storage files: {total_files}\n")
    
    def _show_cleanup_summary(self, deletable_images: List[Dict], args):
        """Show summary of what will be cleaned up."""
        total_size = sum(img['size'] for img in deletable_images)
        print(f"Found {len(deletable_images)} images to delete")
        print(f"Total size: {FileSystemUtils.format_size(total_size)}")
        print(f"Retention: {args.days} days")
        print(f"Include resolved: {'Yes' if args.include_resolved else 'No'}")
        
        if args.dry_run:
            print("\n[DRY RUN] - No files will actually be deleted")
        print()
    
    def _get_user_confirmation(self) -> bool:
        """Get user confirmation before proceeding with deletion."""
        response = input("Proceed with deletion? (y/N): ")
        return response.lower() in ['y', 'yes']
    
    def _perform_cleanup(self, deletable_images: List[Dict], dry_run: bool):
        """Perform the actual cleanup operation."""
        print("\nProcessing...")
        deleted_count = self.file_manager.delete_images(deletable_images, dry_run)
        
        action = "Would delete" if dry_run else "Deleted"
        print(f"\n{action} {deleted_count} images")
        
        if not dry_run:
            print("Cleanup completed successfully!")
        print()

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Clean up fire alert images based on database status",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cleanup_fire_alerts.py --dry-run
  python cleanup_fire_alerts.py --days=14 --include-resolved
  python cleanup_fire_alerts.py --force
        """
    )
    
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be deleted without actually deleting')
    parser.add_argument('--days', type=int, default=7,
                       help='Keep alerts from last N days (default: 7)')
    parser.add_argument('--include-resolved', action='store_true',
                       help='Also delete images from resolved alerts')
    parser.add_argument('--force', action='store_true',
                       help='Skip confirmation prompt')
    
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    app = FireAlertCleanupApp()
    app.run(args)
