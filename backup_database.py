"""
Database Backup Script

Creates a backup of the current database before migration.
Run this before running migrate_db_updated.py
"""

import os
from datetime import datetime
import subprocess

def backup_mysql_database():
    """Create MySQL database backup"""

    # Database configuration - adjust these values
    db_host = "localhost"
    db_user = "root"
    db_password = ""  # Empty password as per user's config
    db_name = "myshop"

    # Create backups directory
    backup_dir = "database_backups"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    # Generate backup filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"{db_name}_backup_{timestamp}.sql"
    backup_path = os.path.join(backup_dir, backup_filename)

    print(f"📦 Creating database backup: {backup_path}")

    try:
        # Use mysqldump to create backup
        cmd = f'mysqldump -h {db_host} -u {db_user} {"-p" + db_password if db_password else ""} {db_name} > "{backup_path}"'

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"✅ Database backup created successfully: {backup_path}")
            print(f"📊 Backup size: {os.path.getsize(backup_path)} bytes")
            return backup_path
        else:
            print(f"❌ Backup failed: {result.stderr}")
            return None

    except Exception as e:
        print(f"❌ Error creating backup: {e}")
        return None

def main():
    print("🛡️ Database Backup Tool")
    print("=" * 40)

    print("⚠️  IMPORTANT: This will create a backup of your current database.")
    print("   Run this BEFORE running the migration script.")
    print("   The backup will be saved in the 'database_backups' folder.")
    print()

    confirm = input("Do you want to create a database backup? (y/N): ").lower().strip()

    if confirm == 'y' or confirm == 'yes':
        backup_path = backup_mysql_database()

        if backup_path:
            print()
            print("🎯 Next steps:")
            print("1. Verify the backup file was created successfully")
            print("2. Run: python migrate_db_updated.py")
            print("3. If migration fails, you can restore from this backup")
        else:
            print("❌ Backup failed. Please check your MySQL configuration.")
    else:
        print("ℹ️ Backup cancelled.")

if __name__ == "__main__":
    main()
