#!/usr/bin/env python3
"""
Database migration script for TTSAI authentication
Adds authentication fields to existing database
"""

import sqlite3
import os
import sys
from pathlib import Path

def backup_database(db_path):
    """Create a backup of the existing database"""
    backup_path = f"{db_path}.backup"
    
    try:
        if os.path.exists(db_path):
            import shutil
            shutil.copy2(db_path, backup_path)
            print(f"✅ Database backed up to: {backup_path}")
            return True
    except Exception as e:
        print(f"❌ Failed to backup database: {e}")
        return False
    
    return True

def migrate_users_table(db_path):
    """Migrate users table to include auth fields"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if auth columns already exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        auth_columns = ['google_id', 'email', 'name', 'profile_picture', 'last_login']
        missing_columns = [col for col in auth_columns if col not in columns]
        
        if not missing_columns:
            print("✅ Users table already has auth columns")
            conn.close()
            return True
        
        print(f"Adding missing columns: {missing_columns}")
        
        # Add missing columns
        for column in missing_columns:
            if column == 'google_id':
                cursor.execute("ALTER TABLE users ADD COLUMN google_id TEXT")
            elif column == 'email':
                cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
            elif column == 'name':
                cursor.execute("ALTER TABLE users ADD COLUMN name TEXT")
            elif column == 'profile_picture':
                cursor.execute("ALTER TABLE users ADD COLUMN profile_picture TEXT")
            elif column == 'last_login':
                cursor.execute("ALTER TABLE users ADD COLUMN last_login TEXT")
        
        # Create indexes for performance
        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
        except sqlite3.Error as e:
            print(f"Warning: Could not create indexes: {e}")
        
        conn.commit()
        conn.close()
        
        print("✅ Users table migrated successfully")
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database migration failed: {e}")
        return False

def create_auth_tables(db_path):
    """Create authentication-related tables"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create user_sessions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_sessions (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            token TEXT,
            created_at TEXT,
            expires_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON user_sessions(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_token ON user_sessions(token)")
        
        conn.commit()
        conn.close()
        
        print("✅ Auth tables created successfully")
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Failed to create auth tables: {e}")
        return False

def verify_migration(db_path):
    """Verify the migration was successful"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check users table structure
        cursor.execute("PRAGMA table_info(users)")
        users_columns = [column[1] for column in cursor.fetchall()]
        
        required_columns = ['id', 'google_id', 'email', 'name', 'profile_picture', 'last_login', 'created_at', 'updated_at']
        missing_columns = [col for col in required_columns if col not in users_columns]
        
        if missing_columns:
            print(f"❌ Missing columns in users table: {missing_columns}")
            return False
        
        # Check user_sessions table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_sessions'")
        if not cursor.fetchone():
            print("❌ user_sessions table not found")
            return False
        
        conn.close()
        
        print("✅ Database migration verified successfully")
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Migration verification failed: {e}")
        return False

def main():
    """Main migration function"""
    print("=== TTSAI Database Migration ===")
    print()
    
    # Find database file
    db_paths = [
        "backend/ttsai.db",
        "ttsai.db",
        "backend/database.db"
    ]
    
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("❌ Database file not found!")
        print("Checked paths:", db_paths)
        sys.exit(1)
    
    print(f"Found database: {db_path}")
    
    # Backup database
    if not backup_database(db_path):
        print("❌ Failed to backup database!")
        sys.exit(1)
    
    # Run migrations
    success = True
    success &= migrate_users_table(db_path)
    success &= create_auth_tables(db_path)
    success &= verify_migration(db_path)
    
    if success:
        print()
        print("🎉 Database migration completed successfully!")
        print()
        print("Next steps:")
        print("1. Test authentication: python test_auth_integration.py")
        print("2. Start backend: cd backend && python app.py")
        print("3. Deploy: python deploy_with_auth.py")
    else:
        print()
        print("❌ Database migration failed!")
        print("Database backup is available for recovery")
        sys.exit(1)

if __name__ == "__main__":
    main()