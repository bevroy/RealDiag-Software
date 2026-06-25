"""
Database Migration Scripts
Migrate from JSON file storage to PostgreSQL/MongoDB
Run: python -m backend.migrations.migrate_to_db
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

# Database connection imports
try:
    import psycopg2
    from psycopg2.extras import Json
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    print("PostgreSQL not available. Install: pip install psycopg2-binary")

try:
    from pymongo import MongoClient
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    print("MongoDB not available. Install: pip install pymongo")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseMigration:
    """Migrate JSON data to production database"""
    
    def __init__(self, db_type: str = "postgresql"):
        self.db_type = db_type
        self.data_dir = Path(__file__).parent.parent.parent / "backend" / "data"
        self.backup_dir = Path(__file__).parent / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
    def backup_json_files(self):
        """Backup existing JSON files before migration"""
        logger.info("📦 Backing up JSON files...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        files_to_backup = [
            "clinical_cases.json",
            "user_progress.json",
            "users.json"
        ]
        
        for filename in files_to_backup:
            source = self.data_dir / filename
            if source.exists():
                dest = self.backup_dir / f"{filename}.{timestamp}.backup"
                with open(source, 'r') as src, open(dest, 'w') as dst:
                    dst.write(src.read())
                logger.info(f"✅ Backed up {filename} to {dest}")
    
    def load_json_data(self, filename: str) -> Any:
        """Load data from JSON file"""
        file_path = self.data_dir / filename
        if not file_path.exists():
            logger.warning(f"⚠️  File not found: {filename}")
            return None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def migrate_to_postgresql(self):
        """Migrate data to PostgreSQL"""
        if not POSTGRES_AVAILABLE:
            raise Exception("psycopg2 not installed")
        
        logger.info("🐘 Starting PostgreSQL migration...")
        
        # Get database credentials from environment
        db_config = {
            'host': os.getenv('DATABASE_HOST', 'localhost'),
            'port': int(os.getenv('DATABASE_PORT', '5432')),
            'database': os.getenv('DATABASE_NAME', 'realdiag_prod'),
            'user': os.getenv('DATABASE_USER', 'realdiag_user'),
            'password': os.getenv('DATABASE_PASSWORD'),
            'sslmode': os.getenv('DATABASE_SSL_MODE', 'require')
        }
        
        if not db_config['password']:
            raise Exception("DATABASE_PASSWORD not set in environment")
        
        # Connect to database
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        
        try:
            # Create tables
            self._create_postgresql_tables(cur)
            
            # Migrate clinical cases
            self._migrate_clinical_cases_pg(cur)
            
            # Migrate users
            self._migrate_users_pg(cur)
            
            # Migrate user progress
            self._migrate_user_progress_pg(cur)
            
            conn.commit()
            logger.info("✅ PostgreSQL migration completed successfully")
            
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Migration failed: {e}")
            raise
        finally:
            cur.close()
            conn.close()
    
    def _create_postgresql_tables(self, cur):
        """Create PostgreSQL schema"""
        logger.info("Creating PostgreSQL tables...")
        
        # Users table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(255) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                username VARCHAR(255) UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                full_name VARCHAR(255),
                role VARCHAR(50) DEFAULT 'user',
                is_active BOOLEAN DEFAULT TRUE,
                is_verified BOOLEAN DEFAULT FALSE,
                mfa_enabled BOOLEAN DEFAULT FALSE,
                mfa_secret TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                failed_login_attempts INTEGER DEFAULT 0,
                account_locked_until TIMESTAMP
            );
        """)
        
        # Clinical cases table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS clinical_cases (
                id SERIAL PRIMARY KEY,
                case_id VARCHAR(255) UNIQUE NOT NULL,
                title TEXT NOT NULL,
                specialty VARCHAR(100) NOT NULL,
                difficulty VARCHAR(50) NOT NULL,
                presentation TEXT NOT NULL,
                history TEXT,
                physical_exam TEXT,
                differential_diagnosis JSONB,
                correct_diagnosis VARCHAR(255),
                explanation TEXT,
                learning_objectives JSONB,
                tags JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # User progress table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_progress (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(255) NOT NULL,
                cases_completed JSONB DEFAULT '[]',
                cases_in_progress JSONB DEFAULT '[]',
                quiz_scores JSONB DEFAULT '{}',
                flashcard_progress JSONB DEFAULT '{}',
                total_study_time_minutes INTEGER DEFAULT 0,
                streak_days INTEGER DEFAULT 0,
                last_activity TIMESTAMP,
                achievements JSONB DEFAULT '[]',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                UNIQUE(user_id)
            );
        """)
        
        # Flashcards table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS flashcards (
                id SERIAL PRIMARY KEY,
                card_id VARCHAR(255) UNIQUE NOT NULL,
                user_id VARCHAR(255) NOT NULL,
                front TEXT NOT NULL,
                back TEXT NOT NULL,
                specialty VARCHAR(100),
                difficulty INTEGER DEFAULT 2,
                interval INTEGER DEFAULT 1,
                ease_factor FLOAT DEFAULT 2.5,
                last_reviewed TIMESTAMP,
                next_review TIMESTAMP,
                review_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            );
        """)
        
        # Sessions table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(255) UNIQUE NOT NULL,
                user_id VARCHAR(255) NOT NULL,
                refresh_token_hash TEXT NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address VARCHAR(45),
                user_agent TEXT,
                is_revoked BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            );
        """)
        
        # Audit log table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(255),
                action VARCHAR(100) NOT NULL,
                resource_type VARCHAR(100),
                resource_id VARCHAR(255),
                details JSONB,
                ip_address VARCHAR(45),
                user_agent TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
            );
        """)
        
        # Create indexes
        cur.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_cases_specialty ON clinical_cases(specialty);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_cases_difficulty ON clinical_cases(difficulty);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_progress_user ON user_progress(user_id);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_flashcards_user ON flashcards(user_id);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_flashcards_next_review ON flashcards(next_review);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_log(user_id);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp);")
        
        logger.info("✅ Tables created successfully")
    
    def _migrate_clinical_cases_pg(self, cur):
        """Migrate clinical cases to PostgreSQL"""
        logger.info("Migrating clinical cases...")
        cases_data = self.load_json_data("clinical_cases.json")
        
        if not cases_data:
            logger.warning("No clinical cases to migrate")
            return
        
        for case in cases_data:
            cur.execute("""
                INSERT INTO clinical_cases 
                (case_id, title, specialty, difficulty, presentation, 
                 correct_diagnosis, explanation, learning_objectives, tags)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (case_id) DO UPDATE SET
                    title = EXCLUDED.title,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                case.get('case_id'),
                case.get('title'),
                case.get('specialty'),
                case.get('difficulty'),
                case.get('presentation'),
                case.get('correct_diagnosis'),
                case.get('explanation'),
                Json(case.get('learning_objectives', [])),
                Json(case.get('tags', []))
            ))
        
        logger.info(f"✅ Migrated {len(cases_data)} clinical cases")
    
    def _migrate_users_pg(self, cur):
        """Migrate users to PostgreSQL"""
        logger.info("Migrating users...")
        users_data = self.load_json_data("users.json")
        
        if not users_data:
            logger.warning("No users to migrate")
            return
        
        for user_id, user in users_data.items():
            cur.execute("""
                INSERT INTO users 
                (user_id, email, username, hashed_password, full_name, 
                 role, is_active, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_id) DO UPDATE SET
                    email = EXCLUDED.email,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                user_id,
                user.get('email'),
                user.get('username'),
                user.get('hashed_password'),
                user.get('full_name'),
                user.get('role', 'user'),
                user.get('is_active', True),
                user.get('created_at', datetime.now())
            ))
        
        logger.info(f"✅ Migrated {len(users_data)} users")
    
    def _migrate_user_progress_pg(self, cur):
        """Migrate user progress to PostgreSQL"""
        logger.info("Migrating user progress...")
        progress_data = self.load_json_data("user_progress.json")
        
        if not progress_data:
            logger.warning("No user progress to migrate")
            return
        
        for user_id, progress in progress_data.items():
            cur.execute("""
                INSERT INTO user_progress 
                (user_id, cases_completed, quiz_scores, flashcard_progress,
                 total_study_time_minutes, streak_days, last_activity)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_id) DO UPDATE SET
                    cases_completed = EXCLUDED.cases_completed,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                user_id,
                Json(progress.get('cases_completed', [])),
                Json(progress.get('quiz_scores', {})),
                Json(progress.get('flashcard_progress', {})),
                progress.get('total_study_time_minutes', 0),
                progress.get('streak_days', 0),
                progress.get('last_activity')
            ))
        
        logger.info(f"✅ Migrated progress for {len(progress_data)} users")
    
    def migrate_to_mongodb(self):
        """Migrate data to MongoDB"""
        if not MONGODB_AVAILABLE:
            raise Exception("pymongo not installed")
        
        logger.info("🍃 Starting MongoDB migration...")
        
        # Get MongoDB URI from environment
        mongodb_uri = os.getenv('MONGODB_URI')
        db_name = os.getenv('MONGODB_DATABASE', 'realdiag_prod')
        
        if not mongodb_uri:
            raise Exception("MONGODB_URI not set in environment")
        
        # Connect to MongoDB
        client = MongoClient(mongodb_uri)
        db = client[db_name]
        
        try:
            # Migrate collections
            self._migrate_clinical_cases_mongo(db)
            self._migrate_users_mongo(db)
            self._migrate_user_progress_mongo(db)
            
            logger.info("✅ MongoDB migration completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            raise
        finally:
            client.close()
    
    def _migrate_clinical_cases_mongo(self, db):
        """Migrate clinical cases to MongoDB"""
        logger.info("Migrating clinical cases...")
        cases_data = self.load_json_data("clinical_cases.json")
        
        if not cases_data:
            logger.warning("No clinical cases to migrate")
            return
        
        collection = db.clinical_cases
        
        # Add timestamps
        for case in cases_data:
            case['created_at'] = datetime.now()
            case['updated_at'] = datetime.now()
        
        # Upsert cases
        for case in cases_data:
            collection.update_one(
                {'case_id': case['case_id']},
                {'$set': case},
                upsert=True
            )
        
        # Create indexes
        collection.create_index('case_id', unique=True)
        collection.create_index('specialty')
        collection.create_index('difficulty')
        
        logger.info(f"✅ Migrated {len(cases_data)} clinical cases")
    
    def _migrate_users_mongo(self, db):
        """Migrate users to MongoDB"""
        logger.info("Migrating users...")
        users_data = self.load_json_data("users.json")
        
        if not users_data:
            logger.warning("No users to migrate")
            return
        
        collection = db.users
        
        # Convert dict to list of users
        users_list = []
        for user_id, user in users_data.items():
            user['user_id'] = user_id
            user['created_at'] = user.get('created_at', datetime.now())
            user['updated_at'] = datetime.now()
            users_list.append(user)
        
        # Upsert users
        for user in users_list:
            collection.update_one(
                {'user_id': user['user_id']},
                {'$set': user},
                upsert=True
            )
        
        # Create indexes
        collection.create_index('user_id', unique=True)
        collection.create_index('email', unique=True)
        collection.create_index('username', unique=True)
        
        logger.info(f"✅ Migrated {len(users_list)} users")
    
    def _migrate_user_progress_mongo(self, db):
        """Migrate user progress to MongoDB"""
        logger.info("Migrating user progress...")
        progress_data = self.load_json_data("user_progress.json")
        
        if not progress_data:
            logger.warning("No user progress to migrate")
            return
        
        collection = db.user_progress
        
        # Convert dict to list
        progress_list = []
        for user_id, progress in progress_data.items():
            progress['user_id'] = user_id
            progress['created_at'] = datetime.now()
            progress['updated_at'] = datetime.now()
            progress_list.append(progress)
        
        # Upsert progress
        for progress in progress_list:
            collection.update_one(
                {'user_id': progress['user_id']},
                {'$set': progress},
                upsert=True
            )
        
        # Create indexes
        collection.create_index('user_id', unique=True)
        
        logger.info(f"✅ Migrated progress for {len(progress_list)} users")
    
    def verify_migration(self):
        """Verify migration completed successfully"""
        logger.info("🔍 Verifying migration...")
        
        if self.db_type == "postgresql":
            self._verify_postgresql()
        elif self.db_type == "mongodb":
            self._verify_mongodb()
    
    def _verify_postgresql(self):
        """Verify PostgreSQL migration"""
        db_config = {
            'host': os.getenv('DATABASE_HOST', 'localhost'),
            'port': int(os.getenv('DATABASE_PORT', '5432')),
            'database': os.getenv('DATABASE_NAME', 'realdiag_prod'),
            'user': os.getenv('DATABASE_USER', 'realdiag_user'),
            'password': os.getenv('DATABASE_PASSWORD')
        }
        
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        
        # Count records
        cur.execute("SELECT COUNT(*) FROM users")
        user_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM clinical_cases")
        case_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM user_progress")
        progress_count = cur.fetchone()[0]
        
        logger.info(f"✅ Verification complete:")
        logger.info(f"   - Users: {user_count}")
        logger.info(f"   - Clinical cases: {case_count}")
        logger.info(f"   - User progress records: {progress_count}")
        
        cur.close()
        conn.close()
    
    def _verify_mongodb(self):
        """Verify MongoDB migration"""
        mongodb_uri = os.getenv('MONGODB_URI')
        db_name = os.getenv('MONGODB_DATABASE', 'realdiag_prod')
        
        client = MongoClient(mongodb_uri)
        db = client[db_name]
        
        user_count = db.users.count_documents({})
        case_count = db.clinical_cases.count_documents({})
        progress_count = db.user_progress.count_documents({})
        
        logger.info(f"✅ Verification complete:")
        logger.info(f"   - Users: {user_count}")
        logger.info(f"   - Clinical cases: {case_count}")
        logger.info(f"   - User progress records: {progress_count}")
        
        client.close()


def main():
    """Main migration script"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Migrate RealDiag data to production database')
    parser.add_argument('--db-type', choices=['postgresql', 'mongodb'], 
                       default='postgresql', help='Target database type')
    parser.add_argument('--backup-only', action='store_true',
                       help='Only backup JSON files without migration')
    parser.add_argument('--verify-only', action='store_true',
                       help='Only verify existing migration')
    
    args = parser.parse_args()
    
    migration = DatabaseMigration(db_type=args.db_type)
    
    try:
        if args.backup_only:
            migration.backup_json_files()
            return
        
        if args.verify_only:
            migration.verify_migration()
            return
        
        # Full migration
        logger.info("=" * 60)
        logger.info("🚀 Starting database migration")
        logger.info(f"Target: {args.db_type}")
        logger.info("=" * 60)
        
        # Backup first
        migration.backup_json_files()
        
        # Migrate
        if args.db_type == "postgresql":
            migration.migrate_to_postgresql()
        elif args.db_type == "mongodb":
            migration.migrate_to_mongodb()
        
        # Verify
        migration.verify_migration()
        
        logger.info("=" * 60)
        logger.info("✅ Migration completed successfully!")
        logger.info("=" * 60)
        logger.info("\nNext steps:")
        logger.info("1. Verify data integrity in production database")
        logger.info("2. Update application to use database instead of JSON files")
        logger.info("3. Keep JSON backups for rollback if needed")
        logger.info("4. Monitor application logs after deployment")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        logger.error("Rollback: Restore from JSON backups if needed")
        sys.exit(1)


if __name__ == "__main__":
    main()
