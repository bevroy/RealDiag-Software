#!/bin/bash
# RealDiag Test Environment Setup Script
# ========================================
# This script sets up the test environment for RealDiag

set -e

echo "🧪 RealDiag Test Environment Setup"
echo "===================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if .env.test exists
if [ ! -f ".env.test" ]; then
    echo -e "${RED}❌ Error: .env.test file not found!${NC}"
    echo "Please create .env.test file first."
    exit 1
fi

# Backup existing .env if it exists
if [ -f ".env" ]; then
    echo -e "${YELLOW}⚠️  Backing up existing .env to .env.backup${NC}"
    cp .env .env.backup
fi

# Copy test environment config
echo "📝 Copying test environment configuration..."
cp .env.test .env

echo -e "${GREEN}✅ Test environment configuration set${NC}"
echo ""

# Ask about database setup
echo "🗄️  Database Setup"
echo "=================="
read -p "Do you want to create a separate test database? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "Enter database name (default: realdiag_test): " DB_NAME
    DB_NAME=${DB_NAME:-realdiag_test}
    
    echo "Creating database: $DB_NAME"
    
    # Try to create database
    if command -v createdb &> /dev/null; then
        createdb $DB_NAME 2>/dev/null || echo "Database already exists or cannot be created"
        echo -e "${GREEN}✅ Database setup complete${NC}"
    else
        echo -e "${YELLOW}⚠️  createdb command not found. Please create database manually:${NC}"
        echo "   createdb $DB_NAME"
    fi
    
    echo ""
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
if [ -d "backend" ]; then
    cd backend
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        echo -e "${GREEN}✅ Backend dependencies installed${NC}"
    fi
    cd ..
else
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        echo -e "${GREEN}✅ Dependencies installed${NC}"
    fi
fi
echo ""

# Install Node dependencies
echo "📦 Installing Node dependencies..."
if [ -d "frontend" ]; then
    cd frontend
    if [ -f "package.json" ]; then
        npm install
        echo -e "${GREEN}✅ Frontend dependencies installed${NC}"
    fi
    cd ..
fi
echo ""

# Check if ports are available
echo "🔍 Checking ports..."
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${YELLOW}⚠️  Port 8000 is already in use${NC}"
    echo "   Please stop the process or use a different port"
else
    echo -e "${GREEN}✅ Port 8000 is available${NC}"
fi

if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${YELLOW}⚠️  Port 3000 is already in use${NC}"
    echo "   Please stop the process or use a different port"
else
    echo -e "${GREEN}✅ Port 3000 is available${NC}"
fi
echo ""

# Create start scripts
echo "📝 Creating start scripts..."

# Backend start script
cat > start_backend_test.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting RealDiag Backend (Test Mode)"
echo "========================================"
cd backend 2>/dev/null || true
export ENVIRONMENT=test
python -m uvicorn main:app --reload --port 8000
EOF
chmod +x start_backend_test.sh

# Frontend start script
cat > start_frontend_test.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting RealDiag Frontend (Test Mode)"
echo "========================================="
cd frontend
export NEXT_PUBLIC_ENVIRONMENT=test
npm run dev
EOF
chmod +x start_frontend_test.sh

echo -e "${GREEN}✅ Start scripts created${NC}"
echo ""

# Summary
echo "✨ Test Environment Setup Complete!"
echo "===================================="
echo ""
echo "🎯 Next Steps:"
echo ""
echo "1. Start Backend (Terminal 1):"
echo "   ${GREEN}./start_backend_test.sh${NC}"
echo "   or"
echo "   ${GREEN}cd backend && uvicorn main:app --reload --port 8000${NC}"
echo ""
echo "2. Start Frontend (Terminal 2):"
echo "   ${GREEN}./start_frontend_test.sh${NC}"
echo "   or"
echo "   ${GREEN}cd frontend && npm run dev${NC}"
echo ""
echo "3. Access the application:"
echo "   Frontend: ${GREEN}http://localhost:3000${NC}"
echo "   Backend API: ${GREEN}http://localhost:8000${NC}"
echo "   API Docs: ${GREEN}http://localhost:8000/docs${NC}"
echo ""
echo "4. Verify test mode is active:"
echo "   ${GREEN}curl http://localhost:8000/health${NC}"
echo "   Should show: \"test_mode\": true"
echo ""
echo "📚 Documentation:"
echo "   ${GREEN}docs/TEST_ENVIRONMENT.md${NC}"
echo ""
echo -e "${YELLOW}⚠️  Remember: This is a TEST environment with FREE access to all features!${NC}"
echo -e "${RED}🔒 NEVER deploy with ENVIRONMENT=test to production!${NC}"
echo ""
