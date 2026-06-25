# Database Migration Strategy - JSON to PostgreSQL
# ================================================

## Current State

RealDiag currently uses in-memory dictionaries for data storage:
- `users_db` - User accounts and profiles
- `sessions_db` - Active user sessions
- `search_history_db` - User search history
- `favorites_db` - User favorite diagnoses
- `custom_lists_db` - User custom differential lists
- `user_settings_db` - User preferences and settings

**Issues with current approach:**
- Data lost on server restart
- No persistence across deployments
- No ACID guarantees
- Cannot scale horizontally
- No backup/recovery mechanism

## Target State: PostgreSQL Database

### Schema Design

```sql
-- Users table
CREATE TABLE users (
    user_id VARCHAR(50) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    specialty VARCHAR(100),
    institution VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    search_count INTEGER DEFAULT 0,
    favorite_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    INDEX idx_email (email),
    INDEX idx_created_at (created_at)
);

-- User settings table
CREATE TABLE user_settings (
    user_id VARCHAR(50) PRIMARY KEY,
    default_specialty VARCHAR(100),
    notification_preferences JSONB,
    display_preferences JSONB,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Search history table
CREATE TABLE search_history (
    search_id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    symptoms JSONB NOT NULL,
    age INTEGER,
    sex VARCHAR(20),
    family VARCHAR(100),
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    result_count INTEGER DEFAULT 0,
    top_diagnosis VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_timestamp (user_id, timestamp DESC)
);

-- Favorites table
CREATE TABLE favorites (
    favorite_id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    rule_id VARCHAR(100) NOT NULL,
    diagnosis_label VARCHAR(255) NOT NULL,
    family VARCHAR(100) NOT NULL,
    notes TEXT,
    added_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_rule (user_id, rule_id),
    INDEX idx_user_added (user_id, added_at DESC)
);

-- Custom lists table
CREATE TABLE custom_lists (
    list_id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    specialty VARCHAR(100),
    diagnoses JSONB DEFAULT '[]',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_public BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_created (user_id, created_at DESC),
    INDEX idx_public (is_public, created_at DESC)
);

-- Refresh tokens table (for secure token rotation)
CREATE TABLE refresh_tokens (
    token_id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    revoked BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_token_hash (token_hash),
    INDEX idx_expires_at (expires_at)
);

-- Audit log table (HIPAA compliance)
CREATE TABLE audit_log (
    log_id SERIAL PRIMARY KEY,
    user_id VARCHAR(50),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id VARCHAR(100),
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_timestamp (user_id, timestamp DESC),
    INDEX idx_action (action),
    INDEX idx_timestamp (timestamp DESC)
);
```

## Migration Strategy

### Phase 1: Setup (Week 1)

1. **Provision PostgreSQL Database**
   ```bash
   # AWS RDS
   aws rds create-db-instance \
     --db-instance-identifier realdiag-prod \
     --db-instance-class db.t3.medium \
     --engine postgres \
     --engine-version 15.3 \
     --master-username realdiag \
     --master-user-password <secure-password> \
     --allocated-storage 100 \
     --storage-encrypted \
     --backup-retention-period 30
   
   # Or use managed PostgreSQL service:
   # - Azure Database for PostgreSQL
   # - Google Cloud SQL
   # - DigitalOcean Managed Databases
   ```

2. **Create Schema**
   ```bash
   psql -h <db-host> -U realdiag -d realdiag_prod -f migrations/001_initial_schema.sql
   ```

3. **Setup Database Connection**
   ```python
   # backend/database/connection.py
   from sqlalchemy import create_engine
   from sqlalchemy.orm import sessionmaker
   import os
   
   DATABASE_URL = os.getenv("DATABASE_URL")
   engine = create_engine(DATABASE_URL, pool_size=20, max_overflow=10)
   SessionLocal = sessionmaker(bind=engine)
   ```

### Phase 2: Dual-Write (Week 2-3)

Run both in-memory and database systems in parallel:

```python
# backend/services/auth_service.py
async def create_user(user_data: UserCreate) -> Dict[str, Any]:
    # Old in-memory system
    users_db[user_id] = user
    
    # New database system (dual-write)
    db = SessionLocal()
    try:
        db_user = User(**user)
        db.add(db_user)
        db.commit()
    except Exception as e:
        logger.error(f"Failed to save to database: {e}")
        # Don't fail if database write fails (yet)
    finally:
        db.close()
    
    return user
```

### Phase 3: Backfill Data (Week 3)

Migrate existing in-memory data to database:

```python
# scripts/migrate_data.py
from backend.database.models import User, SearchHistory, Favorite
from backend.services.auth_service import users_db, search_history_db, favorites_db
from backend.database.connection import SessionLocal

def migrate_users():
    db = SessionLocal()
    try:
        for user_id, user_data in users_db.items():
            db_user = User(**user_data)
            db.add(db_user)
        db.commit()
        print(f"Migrated {len(users_db)} users")
    finally:
        db.close()

def migrate_search_history():
    db = SessionLocal()
    try:
        for user_id, histories in search_history_db.items():
            for history in histories:
                db_history = SearchHistory(**history)
                db.add(db_history)
        db.commit()
        print(f"Migrated search history")
    finally:
        db.close()

if __name__ == "__main__":
    migrate_users()
    migrate_search_history()
    # ... migrate other tables
```

### Phase 4: Read from Database (Week 4)

Switch reads to database while keeping dual-writes:

```python
async def get_user(user_id: str) -> Optional[User]:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        return user
    finally:
        db.close()
```

### Phase 5: Cutover (Week 5)

1. **Final Data Sync**
   - Run migration script one last time
   - Verify data consistency
   - Take full database backup

2. **Switch to Database-Only**
   - Remove in-memory dictionaries
   - All reads and writes go to PostgreSQL
   - Deploy new version

3. **Monitor**
   - Watch error rates
   - Monitor database performance
   - Check for data inconsistencies

### Phase 6: Cleanup (Week 6)

- Remove old in-memory code
- Remove dual-write logic
- Update documentation
- Verify backups working

## Rollback Plan

If migration fails:

1. **Immediate Rollback**
   ```bash
   kubectl rollout undo deployment/realdiag-backend
   ```

2. **Data Recovery**
   - In-memory data still available (dual-write)
   - Restore from database backup if needed

3. **Fix Issues**
   - Investigate root cause
   - Fix database/code issues
   - Retry migration

## Migration Scripts

Create these files in `backend/migrations/`:

```
backend/migrations/
├── 001_initial_schema.sql
├── 002_add_indexes.sql
├── 003_add_audit_log.sql
├── migrate_users.py
├── migrate_search_history.py
├── migrate_favorites.py
├── migrate_custom_lists.py
└── verify_migration.py
```

## Testing Plan

1. **Unit Tests**
   - Test each database model
   - Test CRUD operations
   - Test edge cases

2. **Integration Tests**
   - Test with real PostgreSQL instance
   - Test transaction handling
   - Test concurrent access

3. **Load Testing**
   - Simulate production load
   - Test with 1000+ users
   - Verify performance SLAs

4. **Data Integrity Tests**
   - Verify no data loss
   - Check foreign key constraints
   - Validate JSON fields

## Performance Considerations

1. **Indexing Strategy**
   - Add indexes on foreign keys
   - Index frequently queried columns
   - Composite indexes for common queries

2. **Connection Pooling**
   - Pool size: 20 connections
   - Max overflow: 10
   - Connection timeout: 30s

3. **Query Optimization**
   - Use SQLAlchemy ORM efficiently
   - Eager load relationships
   - Implement pagination

4. **Caching**
   - Redis for session storage
   - Cache frequently accessed data
   - Invalidate on writes

## Security Measures

1. **Encryption**
   - Database encryption at rest
   - TLS connections required
   - Field-level encryption for PHI

2. **Access Control**
   - Least privilege database user
   - Read-only replicas for analytics
   - Audit all data access

3. **Backup & Recovery**
   - Automated daily backups
   - Point-in-time recovery enabled
   - Test restores monthly

## Success Criteria

- [ ] All data successfully migrated
- [ ] Zero data loss
- [ ] Performance meets SLAs (p95 < 200ms)
- [ ] All tests passing
- [ ] Monitoring and alerts configured
- [ ] Backup/restore tested
- [ ] Team trained on new system
- [ ] Documentation updated
- [ ] Rollback plan tested

## Timeline Summary

| Phase | Duration | Key Activities |
|-------|----------|---------------|
| 1. Setup | Week 1 | Provision DB, create schema |
| 2. Dual-Write | Week 2-3 | Write to both systems |
| 3. Backfill | Week 3 | Migrate existing data |
| 4. Read Switch | Week 4 | Read from database |
| 5. Cutover | Week 5 | Database-only mode |
| 6. Cleanup | Week 6 | Remove old code |

**Total: 6 weeks from start to completion**

## Support & Resources

- Database Admin: dba@realdiag.com
- Migration Lead: devops@realdiag.com
- On-call Support: Use PagerDuty
