# PostgreSQL Database Setup Guide

## Quick Start Options

You have three options for adding PostgreSQL to your RealDiag application:

### Option 1: Render.com PostgreSQL (Recommended for Production)
**Best for:** Production deployment, automatic backups, managed service  
**Cost:** Free tier (90 days) or $7/month Starter plan  
**Setup time:** 5 minutes

### Option 2: Local PostgreSQL (Development)
**Best for:** Local development and testing  
**Cost:** Free  
**Setup time:** 10 minutes

### Option 3: Docker PostgreSQL (Development)
**Best for:** Quick local setup without installing PostgreSQL  
**Cost:** Free  
**Setup time:** 2 minutes

---

## Option 1: Render.com PostgreSQL (Production)

### Step 1: Create PostgreSQL Database on Render

1. **Log in to Render**: https://dashboard.render.com/
2. **Create New PostgreSQL**:
   - Click **"New +"** → **"PostgreSQL"**
   - **Name**: `realdiag-database`
   - **Database Name**: `realdiag_prod`
   - **User**: `realdiag_user` (auto-generated)
   - **Region**: `Ohio (US East)` (same region as your backend)
   - **PostgreSQL Version**: `16`
   - **Plan**: 
     - **Free**: 90 days, then expires
     - **Starter**: $7/month, 1GB storage, 1GB RAM
   
3. **Click "Create Database"** (takes ~2 minutes)

### Step 2: Get Database Connection URL

1. Once created, click on your new database
2. Go to the **"Info"** tab
3. Find **"Internal Database URL"** (looks like this):
   ```
   postgresql://realdiag_user:XXX@dpg-XXX.ohio-postgres.render.com/realdiag_prod
   ```
4. **Copy this URL** - you'll need it in the next step

### Step 3: Configure Backend Environment Variable

1. Go to your **Backend Service** in Render Dashboard
2. Click on **"Environment"** tab
3. Click **"Add Environment Variable"**
4. Add:
   ```
   Key:   DATABASE_URL
   Value: <paste the Internal Database URL from Step 2>
   ```
5. **Click "Save Changes"**

Render will automatically redeploy your backend with the database connection!

### Step 4: Verify It's Working

After deployment completes (~3 minutes), check the logs:

1. Go to your backend service → **"Logs"** tab
2. Look for these success messages:
   ```
   ✅ Database engine created successfully
   ✅ Database connection verified
   ✅ Database tables created successfully
   ✅ Using PostgreSQL database for data persistence
   ```

3. Test the API:
   ```bash
   # Create a test account
   curl -X POST https://realdiag-software.onrender.com/users/register \
     -H "Content-Type: application/json" \
     -d '{
       "email": "test@example.com",
       "password": "testpass123",
       "full_name": "Test User"
     }'
   ```

**Done!** Your data is now persistent across restarts. 🎉

---

## Option 2: Local PostgreSQL (Development)

### Step 1: Install PostgreSQL

**macOS:**
```bash
brew install postgresql@16
brew services start postgresql@16
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**Windows:**
- Download installer from: https://www.postgresql.org/download/windows/
- Run installer, keep default settings
- Remember the password you set for the `postgres` user

### Step 2: Create Database

```bash
# Connect to PostgreSQL
psql postgres

# Or on Linux:
sudo -u postgres psql

# Create database and user
CREATE DATABASE realdiag_dev;
CREATE USER realdiag_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE realdiag_dev TO realdiag_user;

# Exit psql
\q
```

### Step 3: Configure Environment Variable

Create a `.env` file in your backend directory:

```bash
# /workspaces/RealDiag-Software/backend/.env
DATABASE_URL=postgresql://realdiag_user:your_secure_password@localhost:5432/realdiag_dev
```

### Step 4: Test Locally

```bash
cd /workspaces/RealDiag-Software/backend
export DATABASE_URL="postgresql://realdiag_user:your_secure_password@localhost:5432/realdiag_dev"
python main.py
```

Check the startup logs for database connection success messages.

---

## Option 3: Docker PostgreSQL (Quick Development Setup)

### Step 1: Run PostgreSQL in Docker

```bash
# Start PostgreSQL container
docker run -d \
  --name realdiag-postgres \
  -e POSTGRES_DB=realdiag_dev \
  -e POSTGRES_USER=realdiag_user \
  -e POSTGRES_PASSWORD=devpassword123 \
  -p 5432:5432 \
  postgres:16-alpine

# Verify it's running
docker ps | grep realdiag-postgres
```

### Step 2: Set Environment Variable

```bash
export DATABASE_URL="postgresql://realdiag_user:devpassword123@localhost:5432/realdiag_dev"
```

### Step 3: Run Backend

```bash
cd /workspaces/RealDiag-Software/backend
python main.py
```

### Useful Docker Commands

```bash
# Stop database
docker stop realdiag-postgres

# Start database
docker start realdiag-postgres

# View logs
docker logs realdiag-postgres

# Delete database (WARNING: deletes all data)
docker rm -f realdiag-postgres
```

---

## Verifying Database Connection

Once you've set up the database using any option above, verify it's working:

### 1. Check Backend Logs

Look for these messages when backend starts:
```
✅ Database engine created successfully
✅ Database connection verified
✅ Database tables created successfully
✅ Using PostgreSQL database for data persistence
```

### 2. Test User Registration

```bash
# Replace localhost:8000 with your backend URL
curl -X POST http://localhost:8000/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "password123",
    "full_name": "Test User",
    "specialty": "cardiology"
  }'
```

### 3. Test Login

```bash
curl -X POST http://localhost:8000/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "password123"
  }'
```

### 4. Check Database Tables

Connect to your database and verify tables were created:

```bash
# For local PostgreSQL
psql -U realdiag_user -d realdiag_dev -c "\dt"

# For Docker PostgreSQL
docker exec -it realdiag-postgres psql -U realdiag_user -d realdiag_dev -c "\dt"
```

You should see tables like:
- `users`
- `sessions`
- `search_history`
- `favorites`
- `custom_lists`
- `user_settings`

---

## Database Schema

Your PostgreSQL database will automatically create these tables:

```sql
-- Users table
users (
  user_id VARCHAR PRIMARY KEY,
  email VARCHAR UNIQUE NOT NULL,
  password_hash VARCHAR NOT NULL,
  full_name VARCHAR NOT NULL,
  specialty VARCHAR,
  institution VARCHAR,
  created_at TIMESTAMP,
  last_login TIMESTAMP,
  is_active BOOLEAN DEFAULT TRUE
)

-- Sessions table
sessions (
  session_id VARCHAR PRIMARY KEY,
  user_id VARCHAR REFERENCES users(user_id),
  access_token VARCHAR UNIQUE NOT NULL,
  refresh_token VARCHAR,
  created_at TIMESTAMP,
  expires_at TIMESTAMP,
  last_activity TIMESTAMP
)

-- Search history
search_history (
  search_id VARCHAR PRIMARY KEY,
  user_id VARCHAR REFERENCES users(user_id),
  symptoms JSON,
  age INTEGER,
  sex VARCHAR,
  family VARCHAR,
  result_count INTEGER,
  top_diagnosis VARCHAR,
  timestamp TIMESTAMP
)

-- Favorites
favorites (
  favorite_id VARCHAR PRIMARY KEY,
  user_id VARCHAR REFERENCES users(user_id),
  rule_id VARCHAR NOT NULL,
  diagnosis_label VARCHAR NOT NULL,
  family VARCHAR,
  notes TEXT,
  added_at TIMESTAMP
)

-- Custom lists
custom_lists (
  list_id VARCHAR PRIMARY KEY,
  user_id VARCHAR REFERENCES users(user_id),
  name VARCHAR NOT NULL,
  description TEXT,
  specialty VARCHAR,
  is_public BOOLEAN DEFAULT FALSE,
  diagnoses JSON,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)

-- User settings
user_settings (
  user_id VARCHAR PRIMARY KEY REFERENCES users(user_id),
  notification_preferences JSON,
  display_preferences JSON,
  updated_at TIMESTAMP
)
```

---

## Troubleshooting

### Error: "connection refused"

**Cause:** PostgreSQL is not running  
**Fix:**
```bash
# macOS
brew services start postgresql@16

# Linux
sudo systemctl start postgresql

# Docker
docker start realdiag-postgres
```

### Error: "authentication failed"

**Cause:** Wrong username/password in DATABASE_URL  
**Fix:** Double-check your DATABASE_URL format:
```
postgresql://USERNAME:PASSWORD@HOST:PORT/DATABASE_NAME
```

### Error: "database does not exist"

**Cause:** Database not created  
**Fix:**
```bash
psql postgres -c "CREATE DATABASE realdiag_dev;"
```

### Error: "sqlalchemy not found"

**Cause:** Dependencies not installed  
**Fix:**
```bash
pip install -r requirements.txt
```

### Backend still using in-memory storage

**Cause:** DATABASE_URL environment variable not set  
**Fix:**
```bash
# Check if it's set
echo $DATABASE_URL

# Set it
export DATABASE_URL="postgresql://..."

# Or add to .env file
echo 'DATABASE_URL="postgresql://..."' >> backend/.env
```

---

## Migration from In-Memory to PostgreSQL

Don't worry about losing data - when you first connect the database, it starts fresh with empty tables. The in-memory data was temporary anyway.

All new user registrations, favorites, search history, etc. will now be saved to PostgreSQL and persist across backend restarts.

---

## Security Best Practices

1. **Never commit DATABASE_URL to git**
   - Add `.env` to `.gitignore`
   - Use Render's environment variables for production

2. **Use strong passwords**
   - Generate random passwords for production databases
   - Don't use "password123" in production!

3. **Restrict database access**
   - Only allow connections from your backend service
   - Use Render's "Internal Database URL" (not External)

4. **Enable SSL in production**
   - Production DATABASE_URL should use `sslmode=require`
   - Example: `postgresql://user:pass@host/db?sslmode=require`

5. **Regular backups**
   - Render provides automatic daily backups on paid plans
   - For local development, use `pg_dump` regularly

---

## Next Steps

After setting up PostgreSQL:

1. ✅ Test user registration and login
2. ✅ Create some favorite diagnoses
3. ✅ Build custom differential lists
4. ✅ Check that data persists after backend restart
5. ✅ Monitor database size and performance
6. Consider setting up database backups
7. Consider adding database migrations for schema changes

Need help? Check the logs or create an issue on GitHub!
