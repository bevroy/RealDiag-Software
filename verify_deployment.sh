#!/bin/bash
# Test Environment Verification Script
# Run this after deployment to verify everything is working

set -e

echo "🧪 RealDiag Test Environment Verification"
echo "=========================================="
echo ""

# Check if URLs are provided
if [ -z "$1" ]; then
    echo "Usage: ./verify_deployment.sh <backend-url>"
    echo ""
    echo "Example:"
    echo "  ./verify_deployment.sh https://realdiag-test-backend.onrender.com"
    echo ""
    exit 1
fi

BACKEND_URL=$1
FRONTEND_URL=${2:-${BACKEND_URL/backend/frontend}}

echo "🔍 Testing Backend: $BACKEND_URL"
echo "🔍 Testing Frontend: $FRONTEND_URL"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test counter
PASSED=0
FAILED=0

# Function to test endpoint
test_endpoint() {
    local name=$1
    local url=$2
    local expected=$3
    
    echo -n "Testing $name... "
    
    response=$(curl -s -w "\n%{http_code}" "$url" 2>/dev/null || echo "000")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "200" ]; then
        if [ -z "$expected" ] || echo "$body" | grep -q "$expected"; then
            echo -e "${GREEN}✓ PASS${NC}"
            ((PASSED++))
            return 0
        else
            echo -e "${RED}✗ FAIL${NC} (unexpected response)"
            echo "  Expected: $expected"
            echo "  Got: $body"
            ((FAILED++))
            return 1
        fi
    else
        echo -e "${RED}✗ FAIL${NC} (HTTP $http_code)"
        ((FAILED++))
        return 1
    fi
}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. Backend Health Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Test health endpoint
if test_endpoint "Health endpoint" "$BACKEND_URL/health" ""; then
    response=$(curl -s "$BACKEND_URL/health")
    
    echo ""
    echo "📋 Health Check Details:"
    echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
    echo ""
    
    # Check for test mode
    if echo "$response" | grep -q '"test_mode".*true'; then
        echo -e "${GREEN}✓ Test mode is ENABLED${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ Test mode is NOT enabled${NC}"
        echo "  ⚠️  Check ENVIRONMENT=test in backend env vars"
        ((FAILED++))
    fi
    
    # Check for subscription bypass
    if echo "$response" | grep -q '"subscriptions_bypassed".*true'; then
        echo -e "${GREEN}✓ Subscriptions are BYPASSED${NC}"
        ((PASSED++))
    else
        echo -e "${YELLOW}⚠ Subscription bypass status unknown${NC}"
    fi
    
    # Check database connection
    if echo "$response" | grep -q '"database".*"connected"'; then
        echo -e "${GREEN}✓ Database is CONNECTED${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ Database connection issue${NC}"
        ((FAILED++))
    fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2. Frontend Accessibility"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL" | grep -q "200"; then
    echo -e "${GREEN}✓ Frontend is accessible${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ Frontend is NOT accessible${NC}"
    ((FAILED++))
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3. API Endpoints"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

test_endpoint "API docs" "$BACKEND_URL/docs" "Swagger"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Results Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "Tests Passed: ${GREEN}$PASSED${NC}"
echo -e "Tests Failed: ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✅ ALL TESTS PASSED!${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "🎉 Your test environment is working correctly!"
    echo ""
    echo "Next steps:"
    echo "1. Visit: $FRONTEND_URL"
    echo "2. Sign up with any email"
    echo "3. Verify you see the yellow test banner"
    echo "4. Test symptom search and diagnostics"
    echo "5. Share URL with beta testers!"
    echo ""
    exit 0
else
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}⚠️  SOME TESTS FAILED${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "1. Check Render dashboard for deployment logs"
    echo "2. Verify environment variables are set correctly"
    echo "3. Wait a few more minutes for services to fully start"
    echo "4. Check database connection string is correct"
    echo ""
    exit 1
fi
