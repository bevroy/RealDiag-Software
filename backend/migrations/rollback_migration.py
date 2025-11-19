"""
Rollback database migration - restore from JSON backups
Run: python -m backend.migrations.rollback_migration
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
import logging
import shutil

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MigrationRollback:
    """Rollback database migration to JSON files"""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent.parent / "backend" / "data"
        self.backup_dir = Path(__file__).parent / "backups"
        
    def list_backups(self):
        """List available backup files"""
        if not self.backup_dir.exists():
            logger.error("❌ No backup directory found")
            return []
        
        backups = {}
        for backup_file in self.backup_dir.glob("*.backup"):
            # Parse filename: clinical_cases.json.20240115_143022.backup
            parts = backup_file.stem.split('.')
            if len(parts) >= 3:
                original_name = f"{parts[0]}.{parts[1]}"
                timestamp = parts[2]
                
                if original_name not in backups:
                    backups[original_name] = []
                backups[original_name].append({
                    'file': backup_file,
                    'timestamp': timestamp
                })
        
        # Sort by timestamp descending
        for name in backups:
            backups[name].sort(key=lambda x: x['timestamp'], reverse=True)
        
        return backups
    
    def restore_latest_backup(self):
        """Restore latest backup files"""
        logger.info("🔄 Starting rollback to JSON files...")
        
        backups = self.list_backups()
        
        if not backups:
            logger.error("❌ No backup files found. Cannot rollback.")
            return False
        
        # Display available backups
        logger.info("\n📦 Available backups:")
        for name, versions in backups.items():
            logger.info(f"  {name}:")
            for version in versions[:3]:  # Show latest 3
                logger.info(f"    - {version['timestamp']}")
        
        # Restore latest version of each file
        restored = []
        for name, versions in backups.items():
            latest = versions[0]
            source = latest['file']
            dest = self.data_dir / name
            
            # Backup current file if exists
            if dest.exists():
                backup_current = dest.with_suffix(f".before_rollback.{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                shutil.copy(dest, backup_current)
                logger.info(f"📦 Backed up current {name} to {backup_current.name}")
            
            # Restore from backup
            shutil.copy(source, dest)
            logger.info(f"✅ Restored {name} from {latest['timestamp']}")
            restored.append(name)
        
        logger.info(f"\n✅ Rollback complete! Restored {len(restored)} files:")
        for name in restored:
            logger.info(f"  - {name}")
        
        logger.info("\n⚠️  Important:")
        logger.info("1. Restart your application to use JSON storage")
        logger.info("2. Update config to point to JSON files instead of database")
        logger.info("3. Database data is NOT deleted - you can re-migrate later")
        
        return True
    
    def restore_specific_backup(self, filename: str, timestamp: str):
        """Restore a specific backup version"""
        backup_file = self.backup_dir / f"{filename}.{timestamp}.backup"
        
        if not backup_file.exists():
            logger.error(f"❌ Backup not found: {backup_file}")
            return False
        
        dest = self.data_dir / filename
        
        # Backup current file
        if dest.exists():
            backup_current = dest.with_suffix(f".before_rollback.{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            shutil.copy(dest, backup_current)
        
        # Restore
        shutil.copy(backup_file, dest)
        logger.info(f"✅ Restored {filename} from {timestamp}")
        
        return True


def main():
    """Main rollback script"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Rollback database migration to JSON files')
    parser.add_argument('--list', action='store_true',
                       help='List available backups')
    parser.add_argument('--file', type=str,
                       help='Specific file to restore (e.g., clinical_cases.json)')
    parser.add_argument('--timestamp', type=str,
                       help='Specific backup timestamp to restore')
    
    args = parser.parse_args()
    
    rollback = MigrationRollback()
    
    if args.list:
        backups = rollback.list_backups()
        if not backups:
            print("No backups found")
            sys.exit(1)
        
        print("\n📦 Available backups:")
        for name, versions in backups.items():
            print(f"\n{name}:")
            for version in versions:
                print(f"  - {version['timestamp']}")
        return
    
    if args.file and args.timestamp:
        success = rollback.restore_specific_backup(args.file, args.timestamp)
        sys.exit(0 if success else 1)
    
    # Full rollback
    logger.info("=" * 60)
    logger.info("🔄 Starting full rollback to JSON storage")
    logger.info("=" * 60)
    
    confirm = input("\n⚠️  This will restore all files from the latest backup.\nContinue? (yes/no): ")
    
    if confirm.lower() != 'yes':
        logger.info("❌ Rollback cancelled")
        sys.exit(0)
    
    success = rollback.restore_latest_backup()
    
    if success:
        logger.info("\n" + "=" * 60)
        logger.info("✅ Rollback completed successfully!")
        logger.info("=" * 60)
    else:
        logger.error("\n❌ Rollback failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
