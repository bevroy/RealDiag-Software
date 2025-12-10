#!/bin/bash
# One-Click Deployment Script for RealDiag Test Environment
# This script guides you through deploying to free hosting platforms

set -e

echo "🚀 RealDiag Test Environment Deployment"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}This script will help you deploy RealDiag to free hosting platforms.${NC}"
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo -e "${YELLOW}⚠️  Git repository not initialized. Initializing...${NC}"
    git init
    git add .
    git commit -m "Initial commit for test environment"
fi

# Check if remote is set
if ! git remote | grep -q "origin"; then
    echo -e "${YELLOW}⚠️  No git remote set.${NC}"
    echo "Please push this repository to GitHub first:"
    echo ""
    echo "1. Create a new repository on GitHub"
    echo "2. Run these commands:"
    echo "   ${GREEN}git remote add origin https://github.com/YOUR_USERNAME/RealDiag-Software.git${NC}"
    echo "   ${GREEN}git branch -M main${NC}"
    echo "   ${GREEN}git push -u origin main${NC}"
    echo ""
    read -p "Press Enter after you've pushed to GitHub..."
fi

echo ""
echo "📋 Deployment Options:"
echo "======================"
echo ""
echo "1. Render.com (Recommended)"
echo "   - Backend + Database + Frontend"
echo "   - One-click deploy with render.yaml"
echo "   - Free tier available"
echo ""
echo "2. Netlify (Frontend) + Render (Backend)"
echo "   - Best for static sites"
echo "   - Automatic deployments"
echo ""
echo "3. Vercel (Frontend) + Railway (Backend)"
echo "   - Great for Next.js"
echo "   - Good free tier"
echo ""

read -p "Choose option (1/2/3): " choice

case $choice in
  1)
    echo ""
    echo -e "${GREEN}✅ Option 1: Render.com Full Stack${NC}"
    echo "===================================="
    echo ""
    echo "Steps to deploy:"
    echo ""
    echo "1. Go to: ${BLUE}https://render.com${NC}"
    echo "2. Sign up/Login with GitHub"
    echo "3. Click ${GREEN}'New +'${NC} → ${GREEN}'Blueprint'${NC}"
    echo "4. Connect this repository"
    echo "5. Render will automatically read render.yaml"
    echo "6. Click ${GREEN}'Apply'${NC}"
    echo "7. Wait 5-10 minutes for deployment"
    echo ""
    echo "Your URLs will be:"
    echo "  Backend:  ${BLUE}https://realdiag-test-api.onrender.com${NC}"
    echo "  Frontend: ${BLUE}https://realdiag-test-frontend.onrender.com${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  After deployment, update frontend to use backend URL${NC}"
    echo ""
    ;;
  
  2)
    echo ""
    echo -e "${GREEN}✅ Option 2: Netlify + Render${NC}"
    echo "=============================="
    echo ""
    echo "Backend (Render):"
    echo "1. Go to: ${BLUE}https://render.com${NC}"
    echo "2. Sign up/Login with GitHub"
    echo "3. Click 'New +' → 'Web Service'"
    echo "4. Connect this repository"
    echo "5. Settings:"
    echo "   - Name: realdiag-test-api"
    echo "   - Root Directory: backend"
    echo "   - Build: pip install -r requirements.txt"
    echo "   - Start: uvicorn main:app --host 0.0.0.0 --port \$PORT"
    echo "6. Add these environment variables:"
    echo "   ENVIRONMENT=test"
    echo "   FREE_ACCESS_TESTING=true"
    echo "   BYPASS_SUBSCRIPTION_CHECKS=true"
    echo "7. Add PostgreSQL database (New + → PostgreSQL)"
    echo "8. Copy database URL to DATABASE_URL variable"
    echo "9. Deploy!"
    echo ""
    echo "Frontend (Netlify):"
    echo "1. Go to: ${BLUE}https://netlify.com${NC}"
    echo "2. Sign up/Login with GitHub"
    echo "3. 'Add new site' → 'Import from Git'"
    echo "4. Connect this repository"
    echo "5. Settings:"
    echo "   - Base: frontend"
    echo "   - Build: npm run build"
    echo "   - Publish: .next"
    echo "6. Environment variable:"
    echo "   NEXT_PUBLIC_API_URL=<your-render-backend-url>"
    echo "   NEXT_PUBLIC_ENVIRONMENT=test"
    echo "7. Deploy!"
    echo ""
    ;;
  
  3)
    echo ""
    echo -e "${GREEN}✅ Option 3: Vercel + Railway${NC}"
    echo "=============================="
    echo ""
    echo "Backend (Railway):"
    echo "1. Go to: ${BLUE}https://railway.app${NC}"
    echo "2. Sign up/Login with GitHub"
    echo "3. 'New Project' → 'Deploy from GitHub'"
    echo "4. Select this repository"
    echo "5. Settings:"
    echo "   - Root: backend"
    echo "   - Start: uvicorn main:app --host 0.0.0.0 --port \$PORT"
    echo "6. Add PostgreSQL: New → Database → PostgreSQL"
    echo "7. Environment variables:"
    echo "   ENVIRONMENT=test"
    echo "   FREE_ACCESS_TESTING=true"
    echo "   BYPASS_SUBSCRIPTION_CHECKS=true"
    echo "   DATABASE_URL=\${{Postgres.DATABASE_URL}}"
    echo "8. Deploy!"
    echo ""
    echo "Frontend (Vercel):"
    echo "1. Go to: ${BLUE}https://vercel.com${NC}"
    echo "2. Sign up/Login with GitHub"
    echo "3. 'Add New...' → 'Project'"
    echo "4. Import this repository"
    echo "5. Settings:"
    echo "   - Framework: Next.js"
    echo "   - Root: frontend"
    echo "6. Environment variables:"
    echo "   NEXT_PUBLIC_API_URL=<your-railway-backend-url>"
    echo "   NEXT_PUBLIC_ENVIRONMENT=test"
    echo "7. Deploy!"
    echo ""
    ;;
  
  *)
    echo -e "${RED}Invalid option${NC}"
    exit 1
    ;;
esac

echo ""
echo "📝 After Deployment:"
echo "==================="
echo ""
echo "1. ✅ Test the health endpoint:"
echo "   ${GREEN}curl https://your-backend-url.com/health${NC}"
echo "   Should show: \"test_mode\": true"
echo ""
echo "2. ✅ Visit your frontend URL"
echo "   Should see yellow test mode banner"
echo ""
echo "3. ✅ Create a test account"
echo "   Sign up with any email"
echo ""
echo "4. ✅ Verify unlimited access"
echo "   All features should be unlocked"
echo ""
echo "5. 📧 Share URL with testers!"
echo "   Send them: ${BLUE}TESTER_ACCESS_GUIDE.md${NC}"
echo ""
echo -e "${YELLOW}⚠️  Important: Save your URLs!${NC}"
echo "   Backend:  _________________________"
echo "   Frontend: _________________________"
echo ""
echo -e "${GREEN}🎉 Ready to deploy! Follow the steps above.${NC}"
echo ""
echo "Need help? Check: ${BLUE}docs/TEST_ENVIRONMENT_DEPLOYMENT.md${NC}"
echo ""
