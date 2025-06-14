#!/usr/bin/env python3
"""
Script to clean up old log files manually.
This can be run periodically to remove old log files.
"""

import os
import glob
from datetime import datetime, timedelta

def cleanup_old_logs(days_to_keep=5):
    """Remove log files older than specified days."""
    try:
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        # Patterns for different log file types
        patterns = [
            "logs/anime_scraper_*.log*",  # New naming pattern
            "logs/scraper_*.log",         # Old naming pattern
        ]
        
        removed_count = 0
        
        for pattern in patterns:
            for log_file in glob.glob(pattern):
                try:
                    file_time = datetime.fromtimestamp(os.path.getctime(log_file))
                    if file_time < cutoff_date:
                        file_size = os.path.getsize(log_file)
                        os.remove(log_file)
                        print(f"Removed: {log_file} ({file_size} bytes, created {file_time.strftime('%Y-%m-%d %H:%M:%S')})")
                        removed_count += 1
                except (OSError, ValueError) as e:
                    print(f"Could not process {log_file}: {e}")
                    continue
        
        if removed_count == 0:
            print("No old log files found to remove.")
        else:
            print(f"\nTotal files removed: {removed_count}")
            
    except Exception as e:
        print(f"Error during cleanup: {e}")

if __name__ == "__main__":
    print("Cleaning up old log files...")
    cleanup_old_logs()
    print("Cleanup completed.")
