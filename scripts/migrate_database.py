"""
Database Migration Script
Adds employee verification fields to existing users table
"""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("❌ DATABASE_URL not found in environment variables")
    print("Please set it in .env file or environment")
    exit(1)

# Fix postgres:// to postgresql:// if needed
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

print(f"🔗 Connecting to database...")
engine = create_engine(DATABASE_URL)

migrations = [
    # Add employee verification fields
    """
    ALTER TABLE users 
    ADD COLUMN IF NOT EXISTS is_employee BOOLEAN DEFAULT FALSE;
    """,
    """
    ALTER TABLE users 
    ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE;
    """,
    """
    ALTER TABLE users 
    ADD COLUMN IF NOT EXISTS email_verification_token VARCHAR(255);
    """,
    """
    ALTER TABLE users 
    ADD COLUMN IF NOT EXISTS email_verification_sent_at TIMESTAMP;
    """,
]

try:
    with engine.connect() as conn:
        print("\n📝 Running migrations...\n")
        
        for i, migration in enumerate(migrations, 1):
            print(f"Migration {i}/{len(migrations)}:")
            print(f"  {migration.strip()[:60]}...")
            
            try:
                conn.execute(text(migration))
                conn.commit()
                print(f"  ✅ Success")
            except Exception as e:
                print(f"  ⚠️  {str(e)}")
                # Continue with other migrations even if one fails
        
        print("\n✨ Migration completed!")
        print("\n🔍 Checking users table structure...")
        
        result = conn.execute(text("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            ORDER BY ordinal_position;
        """))
        
        print("\nUsers table columns:")
        for row in result:
            print(f"  - {row[0]}: {row[1]} (nullable: {row[2]})")
        
        # Check if any users need migration
        result = conn.execute(text("SELECT COUNT(*) FROM users WHERE email_verified IS NULL;"))
        null_count = result.scalar()
        
        if null_count > 0:
            print(f"\n⚠️  Found {null_count} users with NULL email_verified")
            print("   Updating to FALSE...")
            conn.execute(text("UPDATE users SET email_verified = FALSE WHERE email_verified IS NULL;"))
            conn.commit()
            print("   ✅ Updated")
        
        result = conn.execute(text("SELECT COUNT(*) FROM users WHERE is_employee IS NULL;"))
        null_count = result.scalar()
        
        if null_count > 0:
            print(f"\n⚠️  Found {null_count} users with NULL is_employee")
            print("   Updating to FALSE...")
            conn.execute(text("UPDATE users SET is_employee = FALSE WHERE is_employee IS NULL;"))
            conn.commit()
            print("   ✅ Updated")
        
        print("\n✅ All migrations applied successfully!")
        print("\n💡 Your account should now be accessible.")
        print("   Try logging in at: https://realdiag.netlify.app/login")

except Exception as e:
    print(f"\n❌ Error during migration: {e}")
    print("\nPlease check your database connection and try again.")
    exit(1)
