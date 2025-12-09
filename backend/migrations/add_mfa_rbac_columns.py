"""
Database Migration for MFA and RBAC Features

Adds required columns to the users table for:
- Role-based access control (role column)
- Multi-factor authentication (mfa_* columns)

Run this script with: python -m backend.migrations.add_mfa_rbac_columns
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY') or os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: SUPABASE_URL and SUPABASE_KEY environment variables required")
    sys.exit(1)

# SQL migration queries
MIGRATION_SQL = """
-- Add role column for RBAC
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('admin', 'provider', 'user', 'guest'));

-- Add MFA columns
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS mfa_enabled BOOLEAN DEFAULT false;

ALTER TABLE users 
ADD COLUMN IF NOT EXISTS mfa_secret VARCHAR(255);

ALTER TABLE users 
ADD COLUMN IF NOT EXISTS mfa_backup_codes TEXT;

ALTER TABLE users 
ADD COLUMN IF NOT EXISTS mfa_enrolled_at TIMESTAMP;

-- Create index on role for faster RBAC queries
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- Create index on mfa_enabled for faster MFA checks
CREATE INDEX IF NOT EXISTS idx_users_mfa_enabled ON users(mfa_enabled);

-- Update existing users to have 'user' role if NULL
UPDATE users SET role = 'user' WHERE role IS NULL;

-- Add comment documentation
COMMENT ON COLUMN users.role IS 'User role for RBAC: admin, provider, user, or guest';
COMMENT ON COLUMN users.mfa_enabled IS 'Whether two-factor authentication is enabled';
COMMENT ON COLUMN users.mfa_secret IS 'TOTP secret key (base32 encoded)';
COMMENT ON COLUMN users.mfa_backup_codes IS 'JSON array of hashed backup codes';
COMMENT ON COLUMN users.mfa_enrolled_at IS 'Timestamp when MFA was first enabled';
"""

ROLLBACK_SQL = """
-- Rollback migration
DROP INDEX IF EXISTS idx_users_role;
DROP INDEX IF EXISTS idx_users_mfa_enabled;

ALTER TABLE users DROP COLUMN IF EXISTS role;
ALTER TABLE users DROP COLUMN IF EXISTS mfa_enabled;
ALTER TABLE users DROP COLUMN IF EXISTS mfa_secret;
ALTER TABLE users DROP COLUMN IF EXISTS mfa_backup_codes;
ALTER TABLE users DROP COLUMN IF EXISTS mfa_enrolled_at;
"""

def run_migration():
    """Execute the migration"""
    print("Connecting to Supabase...")
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    print("\nRunning migration...")
    print("=" * 60)
    
    try:
        # Execute migration SQL
        result = supabase.rpc('exec_sql', {'query': MIGRATION_SQL}).execute()
        
        print("✓ Migration completed successfully!")
        print("\nAdded columns:")
        print("  - role (VARCHAR, default: 'user')")
        print("  - mfa_enabled (BOOLEAN, default: false)")
        print("  - mfa_secret (VARCHAR)")
        print("  - mfa_backup_codes (TEXT)")
        print("  - mfa_enrolled_at (TIMESTAMP)")
        print("\nCreated indexes:")
        print("  - idx_users_role")
        print("  - idx_users_mfa_enabled")
        
        return True
        
    except Exception as e:
        print(f"✗ Migration failed: {str(e)}")
        print("\nIf using Supabase dashboard SQL editor:")
        print("=" * 60)
        print(MIGRATION_SQL)
        print("=" * 60)
        return False

def rollback_migration():
    """Rollback the migration"""
    print("Connecting to Supabase...")
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    print("\nRolling back migration...")
    print("=" * 60)
    
    try:
        # Execute rollback SQL
        result = supabase.rpc('exec_sql', {'query': ROLLBACK_SQL}).execute()
        
        print("✓ Rollback completed successfully!")
        print("\nRemoved columns:")
        print("  - role")
        print("  - mfa_enabled")
        print("  - mfa_secret")
        print("  - mfa_backup_codes")
        print("  - mfa_enrolled_at")
        
        return True
        
    except Exception as e:
        print(f"✗ Rollback failed: {str(e)}")
        print("\nIf using Supabase dashboard SQL editor:")
        print("=" * 60)
        print(ROLLBACK_SQL)
        print("=" * 60)
        return False

def verify_migration():
    """Verify migration was applied correctly"""
    print("\nVerifying migration...")
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    try:
        # Query to check columns exist
        verify_sql = """
        SELECT column_name, data_type, column_default 
        FROM information_schema.columns 
        WHERE table_name = 'users' 
        AND column_name IN ('role', 'mfa_enabled', 'mfa_secret', 'mfa_backup_codes', 'mfa_enrolled_at')
        ORDER BY column_name;
        """
        
        result = supabase.rpc('exec_sql', {'query': verify_sql}).execute()
        
        print("✓ Verification passed!")
        print("\nDatabase schema updated successfully.")
        
    except Exception as e:
        print(f"✗ Verification failed: {str(e)}")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Database migration for MFA and RBAC')
    parser.add_argument('--rollback', action='store_true', help='Rollback the migration')
    parser.add_argument('--sql-only', action='store_true', help='Print SQL without executing')
    args = parser.parse_args()
    
    if args.sql_only:
        print("Migration SQL:")
        print("=" * 60)
        print(MIGRATION_SQL)
        print("\nRollback SQL:")
        print("=" * 60)
        print(ROLLBACK_SQL)
        sys.exit(0)
    
    if args.rollback:
        success = rollback_migration()
    else:
        success = run_migration()
        if success:
            verify_migration()
    
    sys.exit(0 if success else 1)
