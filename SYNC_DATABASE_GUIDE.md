# Database Sync Guide - Production to Test

## Overview
This guide explains how to sync production database data to your test environment.

## Prerequisites
- PostgreSQL client tools (`pg_dump`, `psql`) installed
- Access to both production and test database connection strings

## Getting Database Connection Strings

### From Render Dashboard:
1. Go to https://dashboard.render.com
2. Select your database
3. Copy the **External Database URL** (not Internal)

### Production Database URL
Your production database connection string from Render

### Test Database URL  
Your test database connection string (created by `realdiag-test-database`)

## Running the Sync

### Step 1: Set Environment Variables
```bash
# Set your production database URL
export PRODUCTION_DATABASE_URL='postgresql://user:password@host:port/dbname'

# Set your test database URL  
export TEST_DATABASE_URL='postgresql://user:password@host:port/dbname'
```

### Step 2: Run the Sync Script
```bash
./sync_production_to_test.sh
```

The script will:
- Dump production database
- Restore to test database
- Clean up temporary files

⚠️ **WARNING**: This will DELETE all existing data in the test database!

## Sync Frequency Recommendations

- **Daily**: If you're actively testing with real data patterns
- **Weekly**: For general testing and QA
- **Before major testing**: Before starting a new test cycle
- **After schema changes**: After updating database structure

## Automated Sync (Optional)

### Using Cron (Linux/Mac)
```bash
# Edit crontab
crontab -e

# Add line to sync daily at 2 AM
0 2 * * * cd /path/to/RealDiag-Software && /bin/bash sync_production_to_test.sh
```

### Using GitHub Actions
Create `.github/workflows/sync-test-db.yml`:
```yaml
name: Sync Test Database
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC
  workflow_dispatch:  # Manual trigger

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - name: Install PostgreSQL client
        run: sudo apt-get install -y postgresql-client
      
      - name: Sync databases
        env:
          PRODUCTION_DATABASE_URL: ${{ secrets.PRODUCTION_DATABASE_URL }}
          TEST_DATABASE_URL: ${{ secrets.TEST_DATABASE_URL }}
        run: |
          pg_dump "$PRODUCTION_DATABASE_URL" --clean --no-owner --no-acl | \
          psql "$TEST_DATABASE_URL"
```

## Troubleshooting

### Connection Errors
- Verify database URLs are correct and include credentials
- Check firewall/network access (Render databases must allow external connections)
- Ensure you're using External Database URLs, not Internal

### Permission Errors
- Make sure your database user has appropriate permissions
- Try adding `--no-owner --no-acl` flags (already included in script)

### Large Database Issues
For databases over 1GB:
```bash
# Use compression
pg_dump "$PRODUCTION_DATABASE_URL" | gzip > backup.sql.gz
gunzip -c backup.sql.gz | psql "$TEST_DATABASE_URL"
```

## Data Privacy Considerations

⚠️ **Important**: The test database will contain real production data including:
- Patient information
- User accounts
- Personal health information

**Recommendations:**
1. Use the same security measures as production
2. Restrict test database access
3. Consider anonymizing sensitive data after sync
4. Never sync production data to publicly accessible test databases

## Anonymizing Data (Optional)

After syncing, you can run anonymization:
```sql
-- Connect to test database
psql "$TEST_DATABASE_URL"

-- Anonymize patient names
UPDATE patients SET 
  first_name = 'Patient',
  last_name = 'Test' || id,
  email = 'test' || id || '@example.com';

-- Anonymize user emails
UPDATE users SET
  email = 'user' || id || '@example.com'
WHERE email NOT LIKE '%@yourdomain.com';
```

## Questions?
If you encounter issues, check:
- Render database logs
- Connection string format
- Network connectivity
- PostgreSQL client version compatibility
