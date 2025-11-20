#!/bin/bash
# Custom Domain Migration Script
# This script helps migrate from Render/Netlify URLs to custom domain

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  RealDiag Custom Domain Setup Wizard${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Prompt for custom domain
read -p "Enter your custom domain (e.g., realdiag.com): " DOMAIN
read -p "Enter your API subdomain (e.g., api): " API_SUBDOMAIN

FULL_DOMAIN="https://${DOMAIN}"
API_DOMAIN="https://${API_SUBDOMAIN}.${DOMAIN}"

echo ""
echo -e "${GREEN}✓${NC} Configuration:"
echo "  Frontend: ${FULL_DOMAIN}"
echo "  API:      ${API_DOMAIN}"
echo ""

# Confirm
read -p "Is this correct? (y/n): " CONFIRM
if [ "$CONFIRM" != "y" ]; then
    echo -e "${RED}✗${NC} Setup cancelled"
    exit 1
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Step 1: DNS Configuration Check${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo "Checking DNS records..."
echo ""

# Check main domain
echo -e "${YELLOW}Checking${NC} ${DOMAIN}..."
if dig +short ${DOMAIN} | grep -q .; then
    echo -e "${GREEN}✓${NC} ${DOMAIN} resolves to: $(dig +short ${DOMAIN} | head -1)"
else
    echo -e "${RED}✗${NC} ${DOMAIN} does not resolve yet"
    echo "  Please configure DNS records and wait for propagation"
fi

# Check API subdomain
echo -e "${YELLOW}Checking${NC} ${API_SUBDOMAIN}.${DOMAIN}..."
if dig +short ${API_SUBDOMAIN}.${DOMAIN} | grep -q .; then
    echo -e "${GREEN}✓${NC} ${API_SUBDOMAIN}.${DOMAIN} resolves to: $(dig +short ${API_SUBDOMAIN}.${DOMAIN} | head -1)"
else
    echo -e "${RED}✗${NC} ${API_SUBDOMAIN}.${DOMAIN} does not resolve yet"
    echo "  Add CNAME record: ${API_SUBDOMAIN} → realdiag-software.onrender.com"
fi

echo ""
read -p "Continue with configuration? (y/n): " CONTINUE
if [ "$CONTINUE" != "y" ]; then
    echo -e "${YELLOW}⚠${NC} Exiting. Run this script again after DNS propagation."
    exit 0
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Step 2: Update Environment Configuration${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Create .env.production if it doesn't exist
if [ ! -f .env.production ]; then
    echo "Creating .env.production..."
    cp .env.production.template .env.production
fi

# Update .env.production
echo "Updating .env.production..."
sed -i.bak "s|API_BASE_URL=.*|API_BASE_URL=${API_DOMAIN}|g" .env.production
sed -i.bak "s|FRONTEND_URL=.*|FRONTEND_URL=${FULL_DOMAIN}|g" .env.production
sed -i.bak "s|CORS_ORIGINS=.*|CORS_ORIGINS=${FULL_DOMAIN},https://www.${DOMAIN}|g" .env.production

echo -e "${GREEN}✓${NC} .env.production updated"

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Step 3: Environment Variables to Set${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "RENDER ENVIRONMENT VARIABLES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Go to: https://dashboard.render.com"
echo "Select: realdiag-software service"
echo "Navigate: Environment tab"
echo ""
echo "Add/Update these variables:"
echo ""
echo "CORS_ORIGINS=${FULL_DOMAIN},https://www.${DOMAIN}"
echo "FRONTEND_URL=${FULL_DOMAIN}"
echo "API_BASE_URL=${API_DOMAIN}"
echo "ENVIRONMENT=production"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "NETLIFY ENVIRONMENT VARIABLES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Go to: https://app.netlify.com"
echo "Select: Your RealDiag site"
echo "Navigate: Site settings → Environment variables"
echo ""
echo "Add/Update these variables:"
echo ""
echo "NEXT_PUBLIC_API_URL=${API_DOMAIN}"
echo "NEXT_PUBLIC_API_BASE=${API_DOMAIN}"
echo "NEXT_PUBLIC_ENVIRONMENT=production"
echo ""

read -p "Press Enter after you've updated the environment variables..."

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Step 4: Custom Domain Configuration${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "NETLIFY CUSTOM DOMAIN"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Go to: https://app.netlify.com"
echo "2. Select your RealDiag site"
echo "3. Click: Domain settings"
echo "4. Click: Add custom domain"
echo "5. Enter: ${DOMAIN}"
echo "6. Follow verification steps"
echo "7. Add domain alias: www.${DOMAIN}"
echo "8. Enable: Force HTTPS"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "RENDER CUSTOM DOMAIN"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Go to: https://dashboard.render.com"
echo "2. Select: realdiag-software service"
echo "3. Navigate: Settings tab"
echo "4. Scroll to: Custom Domains"
echo "5. Click: Add Custom Domain"
echo "6. Enter: ${API_SUBDOMAIN}.${DOMAIN}"
echo "7. Click: Verify"
echo "8. Wait for SSL certificate provisioning"
echo ""

read -p "Press Enter after you've configured custom domains..."

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Step 5: Testing Configuration${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo "Testing API endpoint..."
if curl -f -s ${API_DOMAIN}/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} API is responding at ${API_DOMAIN}/health"
else
    echo -e "${RED}✗${NC} API is not responding yet at ${API_DOMAIN}/health"
    echo "  This may take 5-10 minutes for SSL provisioning"
fi

echo ""
echo "Testing frontend..."
if curl -f -s ${FULL_DOMAIN} > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Frontend is responding at ${FULL_DOMAIN}"
else
    echo -e "${RED}✗${NC} Frontend is not responding yet at ${FULL_DOMAIN}"
    echo "  This may take a few minutes for DNS/SSL propagation"
fi

echo ""
echo "Checking SSL certificates..."
echo -e "${YELLOW}Frontend SSL:${NC}"
echo | openssl s_client -servername ${DOMAIN} -connect ${DOMAIN}:443 2>/dev/null | openssl x509 -noout -issuer -dates 2>/dev/null | grep -E "issuer|notAfter" || echo "  SSL not ready yet"

echo ""
echo -e "${YELLOW}API SSL:${NC}"
echo | openssl s_client -servername ${API_SUBDOMAIN}.${DOMAIN} -connect ${API_SUBDOMAIN}.${DOMAIN}:443 2>/dev/null | openssl x509 -noout -issuer -dates 2>/dev/null | grep -E "issuer|notAfter" || echo "  SSL not ready yet"

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Step 6: Final Verification${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo "Redeploy to apply changes:"
echo ""
echo "git add ."
echo "git commit -m \"Configure custom domain: ${DOMAIN}\""
echo "git push"
echo ""

echo "Manual verification steps:"
echo ""
echo "1. Open: ${FULL_DOMAIN}"
echo "2. Check browser console for errors"
echo "3. Test symptom search functionality"
echo "4. Verify API calls go to: ${API_DOMAIN}"
echo "5. Check Sentry dashboard for any errors"
echo ""

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  Setup Complete!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Your production URLs:"
echo "  Website: ${FULL_DOMAIN}"
echo "  API:     ${API_DOMAIN}"
echo "  Docs:    ${API_DOMAIN}/docs"
echo ""
echo "Next steps:"
echo "  • Monitor Sentry for 24 hours"
echo "  • Submit sitemap to Google Search Console"
echo "  • Set up uptime monitoring"
echo "  • Update documentation"
echo ""
echo -e "${YELLOW}Note:${NC} DNS propagation can take up to 48 hours globally"
echo ""
