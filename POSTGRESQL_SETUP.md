# PostgreSQL Database Setup Guide

## Overview
This guide walks you through setting up a PostgreSQL database for RealDiag on Render.

## Step 1: Create PostgreSQL Database on Render

1. **Log into Render Dashboard**
   - Go to https://dashboard.render.com/
   - Sign in with your GitHub account

2. **Create New PostgreSQL Instance**
   - Click "New +" button in top right
   - Select "PostgreSQL"
   - Configure database:
     - **Name**: `realdiag-database`
     - **Database**: `realdiag_prod`
     - **User**: `realdiag_user` (auto-generated)
     - **Region**: Same as backend (Ohio US East)
     - **PostgreSQL Version**: 16 (latest stable)
     - **Plan**: Free tier (0 GB, limited to 90 days) or Starter ($7/month, 1 GB)

3. **Wait for Deployment**
   - Database creation takes ~2 minutes
   - Status will change from "Creating" to "Available"

4. **Copy Connection Details**
   - After creation, click on the database
   - Go to "Info" tab
   - Copy the following values:
     - **Internal Database URL**: Use this (faster, private network)
     - **External Database URL**: Fallback for local development

   Example format:
   ```
   postgres://realdiag_user:password@dpg-xxxxx.ohio-postgres.render.com/realdiag_prod
   ```

## Step 2: Add DATABASE_URL to Backend Environment Variables

1. **Navigate to Backend Service**
   - Go to Render Dashboard → Services
   - Click on your backend service (`realdiag-software`)

2. **Add Environment Variable**
   - Click "Environment" tab
   - Click "Add Environment Variable"
   - Add the following:
     ```
     Key: DATABASE_URL
     Value: <paste Internal Database URL from Step 1>
     ```

3. **Alternative: Individual Variables**
   If you prefer separate variables:
   ```
   DATABASE_HOST=dpg-xxxxx.ohio-postgres.render.com
   DATABASE_PORT=5432
   DATABASE_NAME=realdiag_prod
   DATABASE_USER=realdiag_user
   DATABASE_PASSWORD=<your_password>
   DATABASE_SSL_MODE=require
   ```

4. **Save and Redeploy**
   - Click "Save Changes"
   - Backend will auto-redeploy with new environment variables

## Step 3: Install PostgreSQL Dependencies

The following packages are already in `requirements.txt`:
- `psycopg2-binary` - PostgreSQL adapter
- `sqlalchemy` - ORM for database operations

If missing, add them:
```bash
pip install psycopg2-binary sqlalchemy
```

## Step 4: Test Database Connection

Once the database module is created, test the connection:

```bash
# From backend directory
python -c "from services.database import engine; print('✅ Database connected successfully')"
```

## Step 5: Run Migration Script

After database.py is created and connection is verified:

```bash
# From backend directory
python migrations/migrate_to_db.py
```

This will:
- Create all required tables (users, sessions, search_history, etc.)
- Migrate any existing user data from in-memory storage
- Create backup of existing data

## Connection String Format

PostgreSQL connection strings follow this format:
```
postgresql://username:password@host:port/database_name?sslmode=require
```

Example:
```
postgresql://realdiag_user:abc123xyz@dpg-abc123.ohio-postgres.render.com:5432/realdiag_prod?sslmode=require
```

## Database Schema

The migration will create these tables:

### users
- `id` (serial primary key)
- `user_id` (varchar, unique)
- `email` (varchar, unique)
- `username` (varchar, unique)
- `hashed_password` (text)
- `full_name` (varchar)
- `specialty` (varchar)
- `institution` (varchar)
- `role` (varchar, default: 'user')
- `is_active` (boolean, default: true)
- `created_at` (timestamp)
- `last_login` (timestamp)
- `search_count` (integer, default: 0)
- `favorite_count` (integer, default: 0)

### sessions
- `id` (serial primary key)
- `session_id` (varchar, unique)
- `user_id` (varchar, foreign key)
- `token` (text)
- `expires_at` (timestamp)
- `created_at` (timestamp)

### search_history
- `id` (serial primary key)
- `search_id` (varchar, unique)
- `user_id` (varchar, foreign key)
- `symptoms` (jsonb)
- `age` (integer)
- `sex` (varchar)
- `family` (varchar)
- `timestamp` (timestamp)
- `result_count` (integer)
- `top_diagnosis` (varchar)

### favorites
- `id` (serial primary key)
- `favorite_id` (varchar, unique)
- `user_id` (varchar, foreign key)
- `rule_id` (varchar)
- `diagnosis_label` (varchar)
- `family` (varchar)
- `notes` (text)
- `added_at` (timestamp)

### custom_lists
- `id` (serial primary key)
- `list_id` (varchar, unique)
- `user_id` (varchar, foreign key)
- `name` (varchar)
- `description` (text)
- `specialty` (varchar)
- `diagnoses` (jsonb)
- `created_at` (timestamp)
- `updated_at` (timestamp)
- `is_public` (boolean, default: false)

### user_settings
- `id` (serial primary key)
- `user_id` (varchar, unique, foreign key)
- `default_specialty` (varchar)
- `notification_preferences` (jsonb)
- `display_preferences` (jsonb)

## Troubleshooting

### Connection Refused
- Verify DATABASE_URL is correct
- Ensure database is in "Available" state on Render
- Check SSL mode is set to `require`

### Authentication Failed
- Double-check username and password
- Copy connection string exactly from Render dashboard

### SSL Certificate Error
- Add `?sslmode=require` to connection string
- Use Internal Database URL (not External)

### Migration Errors
- Ensure database is empty (no conflicting tables)
- Check all environment variables are set
- Review migration logs for specific errors

## Next Steps

After database setup:
1. ✅ Create database.py module
2. ✅ Update auth_service.py to use database
3. ✅ Run migration script
4. ✅ Test user registration and login
5. ✅ Deploy to production
6. ✅ Monitor with Sentry for any database errors

## Security Notes

- DATABASE_URL contains sensitive credentials - never commit to git
- Use environment variables for all database configuration
- SSL mode is required for Render PostgreSQL connections
- Render automatically manages SSL certificates
- Database is only accessible from Render services (internal network) or whitelisted IPs

## Backup and Recovery

Render provides automatic daily backups on paid plans:
- **Free tier**: Manual snapshots only
- **Starter ($7/month)**: 7-day retention
- **Standard ($20/month)**: 30-day retention

To create manual backup:
```bash
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql
```

To restore from backup:
```bash
psql $DATABASE_URL < backup_file.sql
```
