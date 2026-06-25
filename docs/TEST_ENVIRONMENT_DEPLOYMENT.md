# Test Environment Deployment Guide

## 🚀 Deploying RealDiag Test Environment

This guide explains how to deploy the test environment so testers can access it via a web URL.

## Deployment Options

### Option 1: Render.com (Recommended - Free Tier)

#### Backend Deployment

1. **Create Render Account**
   - Go to https://render.com
   - Sign up with GitHub

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name**: `realdiag-test-api`
     - **Environment**: `Python 3`
     - **Build Command**: `pip install -r backend/requirements.txt`
     - **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
     - **Plan**: Free

3. **Set Environment Variables**
   ```
   ENVIRONMENT=test
   FREE_ACCESS_TESTING=true
   BYPASS_SUBSCRIPTION_CHECKS=true
   DATABASE_URL=<your_postgres_url>
   ```

4. **Add PostgreSQL Database**
   - Click "New +" → "PostgreSQL"
   - Name: `realdiag-test-db`
   - Plan: Free
   - Copy the internal database URL to `DATABASE_URL`

5. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (5-10 minutes)
   - Note your API URL: `https://realdiag-test-api.onrender.com`

#### Frontend Deployment

1. **Create New Static Site**
   - Click "New +" → "Static Site"
   - Connect your repository
   - Configure:
     - **Name**: `realdiag-test`
     - **Build Command**: `cd frontend && npm install && npm run build`
     - **Publish Directory**: `frontend/out` or `frontend/.next`

2. **Set Environment Variables**
   ```
   NEXT_PUBLIC_API_URL=https://realdiag-test-api.onrender.com
   NEXT_PUBLIC_ENVIRONMENT=test
   ```

3. **Deploy**
   - Click "Create Static Site"
   - Your URL: `https://realdiag-test.onrender.com`

**Share this URL with testers!**

---

### Option 2: Netlify (Frontend) + Render (Backend)

#### Backend on Render
Follow Option 1 backend steps above.

#### Frontend on Netlify

1. **Create Netlify Account**
   - Go to https://netlify.com
   - Sign up with GitHub

2. **New Site from Git**
   - Click "Add new site" → "Import an existing project"
   - Choose GitHub, select repository

3. **Build Settings**
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `frontend/.next` or `frontend/out`

4. **Environment Variables**
   ```
   NEXT_PUBLIC_API_URL=https://realdiag-test-api.onrender.com
   NEXT_PUBLIC_ENVIRONMENT=test
   ```

5. **Deploy**
   - Your URL: `https://realdiag-test.netlify.app`

---

### Option 3: Vercel (Frontend) + Railway (Backend)

#### Backend on Railway

1. **Create Railway Account**
   - Go to https://railway.app
   - Sign up with GitHub

2. **New Project**
   - Click "New Project"
   - Choose "Deploy from GitHub repo"
   - Select your repository

3. **Configure Service**
   - **Root Directory**: `backend`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. **Add PostgreSQL**
   - Click "New" → "Database" → "PostgreSQL"
   - Copy connection URL

5. **Environment Variables**
   ```
   ENVIRONMENT=test
   FREE_ACCESS_TESTING=true
   BYPASS_SUBSCRIPTION_CHECKS=true
   DATABASE_URL=${{Postgres.DATABASE_URL}}
   ```

6. **Deploy**
   - Railway generates URL automatically
   - Example: `https://realdiag-test-production.up.railway.app`

#### Frontend on Vercel

1. **Create Vercel Account**
   - Go to https://vercel.com
   - Sign up with GitHub

2. **Import Project**
   - Click "Add New..." → "Project"
   - Import GitHub repository

3. **Configure Project**
   - **Framework**: Next.js (auto-detected)
   - **Root Directory**: `frontend`

4. **Environment Variables**
   ```
   NEXT_PUBLIC_API_URL=https://realdiag-test-production.up.railway.app
   NEXT_PUBLIC_ENVIRONMENT=test
   ```

5. **Deploy**
   - Your URL: `https://realdiag-test.vercel.app`

---

### Option 4: AWS / DigitalOcean / Linode (Production-Ready)

For more control and production-like testing:

#### Requirements
- Ubuntu 20.04+ server
- 2GB RAM minimum
- Domain name (optional but recommended)

#### Setup Script

SSH into your server and run:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3-pip postgresql nginx nodejs npm git

# Clone repository
git clone https://github.com/bevroy/RealDiag-Software.git
cd RealDiag-Software

# Setup backend
cd backend
pip3 install -r requirements.txt

# Create database
sudo -u postgres createdb realdiag_test

# Configure environment
cp ../.env.test .env
# Edit .env with your database credentials

# Setup frontend
cd ../frontend
npm install
npm run build

# Install PM2 for process management
sudo npm install -g pm2

# Start backend
cd ../backend
pm2 start "uvicorn main:app --host 0.0.0.0 --port 8000" --name realdiag-api

# Start frontend
cd ../frontend
pm2 start "npm start" --name realdiag-frontend

# Configure Nginx
sudo tee /etc/nginx/sites-available/realdiag-test << EOF
server {
    listen 80;
    server_name test.yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/realdiag-test /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Setup SSL (optional but recommended)
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d test.yourdomain.com
```

---

## 🔐 Security Considerations for Test Environment

### Required Settings

✅ **Keep These Enabled:**
- User authentication
- Password hashing
- HTTPS/SSL (in production deployment)
- Input validation
- CORS restrictions

❌ **Safe to Disable:**
- Payment processing
- Rate limiting (or set very high)
- Subscription checks
- Premium feature gates
- Email verification (optional)

### Environment Variables Checklist

```bash
# Test mode flags
ENVIRONMENT=test
FREE_ACCESS_TESTING=true
BYPASS_SUBSCRIPTION_CHECKS=true

# Security (keep enabled)
JWT_SECRET=<generate_random_secret>
PASSWORD_HASH_ROUNDS=12

# Features (disabled for testing)
STRIPE_ENABLED=false
RATE_LIMIT_ENABLED=false
EMAIL_VERIFICATION_REQUIRED=false

# Monitoring (optional)
SENTRY_DSN=<optional_for_error_tracking>
```

---

## 📧 Inviting Testers

### Email Template

Subject: **You're Invited to Beta Test RealDiag! 🎉**

```
Hi [Name],

You've been selected to participate in the RealDiag beta testing program!

🌐 Access URL: https://test.realdiag.com
📖 Tester Guide: https://github.com/bevroy/RealDiag-Software/blob/main/TESTER_ACCESS_GUIDE.md

Getting Started:
1. Visit the URL above
2. Click "Sign Up" and create an account
3. All features are unlocked - no payment needed!
4. Start exploring and testing

What to Test:
✓ Symptom search accuracy
✓ Diagnostic recommendations
✓ User interface and navigation
✓ Mobile responsiveness
✓ Any bugs or issues

Report Issues:
- Email: testing@realdiag.com
- GitHub: https://github.com/bevroy/RealDiag-Software/issues

Important:
⚠️ This is a TEST ENVIRONMENT - not for real medical use
⚠️ Data may be reset periodically
⚠️ Do not enter real patient information

Thank you for helping us make RealDiag better!

Questions? Reply to this email or contact testing@realdiag.com

Best regards,
The RealDiag Team
```

---

## 📊 Monitoring Your Test Environment

### Check Health Status

```bash
curl https://test.realdiag.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "environment": "test",
  "test_mode": true
}
```

### Monitor Logs

#### Render
- Dashboard → Your Service → Logs tab

#### Railway
- Dashboard → Your Service → Deployments → View Logs

#### PM2 (Self-hosted)
```bash
pm2 logs realdiag-api
pm2 logs realdiag-frontend
```

### Usage Analytics

Track tester activity:
- Number of sign-ups
- Features used most
- Error rates
- Page load times

Consider adding:
- Google Analytics
- Mixpanel
- PostHog (open source)

---

## 🔄 Updating the Test Environment

### Git Push Auto-Deploy

Most platforms support automatic deployments:

1. **Make changes locally**
   ```bash
   git add .
   git commit -m "Fix symptom search bug"
   git push origin main
   ```

2. **Auto-deploy triggers**
   - Render: Automatic on push
   - Vercel: Automatic on push
   - Railway: Automatic on push
   - Netlify: Automatic on push

3. **Notify testers**
   - Email: "New features/fixes deployed!"
   - In-app: Update notification

### Manual Deployment

For self-hosted:

```bash
# SSH into server
ssh user@your-server

# Pull latest changes
cd RealDiag-Software
git pull origin main

# Update backend
cd backend
pip3 install -r requirements.txt
pm2 restart realdiag-api

# Update frontend
cd ../frontend
npm install
npm run build
pm2 restart realdiag-frontend
```

---

## 🧪 Testing Checklist Before Sharing

Before giving access to testers:

- [ ] Environment variables set correctly
- [ ] Test mode banner visible
- [ ] Health endpoint returns test_mode: true
- [ ] Can create new account
- [ ] Can log in
- [ ] All features accessible without payment
- [ ] No rate limiting issues
- [ ] API responds quickly (< 500ms)
- [ ] Mobile site works
- [ ] SSL/HTTPS working (if applicable)
- [ ] Error pages display properly
- [ ] Database backups configured

---

## 💰 Cost Estimates

### Free Tier Options (0-10 testers)

| Platform | Frontend | Backend | Database | Total |
|----------|----------|---------|----------|-------|
| Render + Render | Free | Free | Free | $0/mo |
| Netlify + Render | Free | Free | Free | $0/mo |
| Vercel + Railway | Free | Free | Free | $0/mo |

**Limitations:**
- Limited compute hours
- Slower cold starts
- Basic support

### Paid Options (10+ testers)

| Platform | Frontend | Backend | Database | Total |
|----------|----------|---------|----------|-------|
| Render | $7/mo | $7/mo | $7/mo | $21/mo |
| DigitalOcean | - | $12/mo | Included | $12/mo |
| AWS Lightsail | - | $10/mo | $15/mo | $25/mo |

**Benefits:**
- Better performance
- More resources
- 24/7 availability

---

## 📞 Support During Testing

### Monitoring Support Requests

Set up:
1. **Email**: testing@realdiag.com (forward to your email)
2. **GitHub Issues**: Enable issue templates
3. **Slack/Discord**: Create testing channel (optional)

### Response Time Targets
- Critical bugs: 4 hours
- High priority: 24 hours
- Medium priority: 3 days
- Low priority: 1 week

### Support Workflow
1. Tester reports issue
2. Acknowledge receipt (within 24h)
3. Investigate and reproduce
4. Fix and deploy
5. Notify tester fix is deployed
6. Tester verifies fix

---

## 🎯 Success Metrics

Track these during testing:

### Engagement
- Daily active users
- Session duration
- Features used
- Return rate

### Quality
- Bugs reported
- Critical bugs found
- Bugs fixed
- User satisfaction

### Performance
- Page load times
- API response times
- Error rates
- Uptime

---

**Need help with deployment? Contact: support@realdiag.com**
