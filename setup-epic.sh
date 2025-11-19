#!/bin/bash

# RealDiag Epic Integration Setup Script
# This script helps configure your environment for Epic/EHR integration

set -e

echo "=================================="
echo "RealDiag Epic Integration Setup"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running in backend directory
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}Error: requirements.txt not found.${NC}"
    echo "Please run this script from the backend directory."
    exit 1
fi

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo -e "${RED}Error: Python 3.8 or higher is required.${NC}"
    echo "Current version: $PYTHON_VERSION"
    exit 1
fi

echo -e "${GREEN}✓ Python $PYTHON_VERSION detected${NC}"
echo ""

# Check if in virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}Warning: Not in a virtual environment.${NC}"
    echo "It's recommended to use a virtual environment."
    echo ""
    read -p "Create and activate a virtual environment? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
        source venv/bin/activate
        echo -e "${GREEN}✓ Virtual environment created and activated${NC}"
        echo ""
    fi
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Check if installation was successful
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Python dependencies installed successfully${NC}"
else
    echo -e "${RED}✗ Failed to install Python dependencies${NC}"
    exit 1
fi
echo ""

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}✓ .env file created${NC}"
        echo -e "${YELLOW}⚠ Please edit .env with your Epic credentials${NC}"
    else
        echo -e "${RED}✗ .env.example not found${NC}"
    fi
else
    echo -e "${YELLOW}⚠ .env file already exists, skipping...${NC}"
fi
echo ""

# Check for required environment variables
echo "Checking Epic integration configuration..."
MISSING_VARS=()

if [ -f ".env" ]; then
    source .env
    
    if [ -z "$FHIR_BASE_URL" ] || [ "$FHIR_BASE_URL" = "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4" ]; then
        MISSING_VARS+=("FHIR_BASE_URL (using default)")
    fi
    
    if [ -z "$SMART_CLIENT_ID" ] || [ "$SMART_CLIENT_ID" = "CHANGE_ME_TO_EPIC_CLIENT_ID" ]; then
        MISSING_VARS+=("SMART_CLIENT_ID")
    fi
    
    if [ -z "$SMART_CLIENT_SECRET" ] || [ "$SMART_CLIENT_SECRET" = "CHANGE_ME_TO_EPIC_CLIENT_SECRET" ]; then
        MISSING_VARS+=("SMART_CLIENT_SECRET")
    fi
    
    if [ ${#MISSING_VARS[@]} -gt 0 ]; then
        echo -e "${YELLOW}⚠ The following environment variables need configuration:${NC}"
        for var in "${MISSING_VARS[@]}"; do
            echo "  - $var"
        done
        echo ""
        echo "To complete Epic integration setup:"
        echo "1. Register at: https://apporchard.epic.com/"
        echo "2. Edit .env with your Epic credentials"
        echo "3. Run this script again to verify"
    else
        echo -e "${GREEN}✓ All required environment variables configured${NC}"
    fi
else
    echo -e "${RED}✗ .env file not found${NC}"
    echo "Please create .env file with Epic credentials"
fi
echo ""

# Test imports
echo "Testing FHIR integration modules..."
IMPORT_TEST=$(python3 << END
import sys
try:
    from backend.services.fhir_client import FHIRClient
    from backend.services.smart_diagnostic_engine import SmartDiagnosticEngine
    from backend.services.smart_router import router as smart_router
    print("SUCCESS")
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
END
)

if [ "$IMPORT_TEST" = "SUCCESS" ]; then
    echo -e "${GREEN}✓ FHIR integration modules loaded successfully${NC}"
else
    echo -e "${RED}✗ Failed to load FHIR integration modules${NC}"
    echo "$IMPORT_TEST"
    exit 1
fi
echo ""

# Summary
echo "=================================="
echo "Setup Summary"
echo "=================================="
echo ""
echo -e "${GREEN}✓ Python dependencies installed${NC}"
echo -e "${GREEN}✓ FHIR integration modules verified${NC}"

if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    echo -e "${YELLOW}⚠ Epic credentials need configuration${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Register your app at https://apporchard.epic.com/"
    echo "2. Edit .env with credentials:"
    echo "   - SMART_CLIENT_ID"
    echo "   - SMART_CLIENT_SECRET"
    echo "   - SMART_REDIRECT_URI"
    echo "3. Start the backend:"
    echo "   python -m uvicorn backend.main:app --reload"
else
    echo -e "${GREEN}✓ Epic integration configured${NC}"
    echo ""
    echo "Ready to start! Run:"
    echo "  python -m uvicorn backend.main:app --reload"
fi

echo ""
echo "For complete documentation, see:"
echo "  - EPIC_INTEGRATION_GUIDE.md"
echo "  - .env.example (configuration reference)"
echo ""
echo "=================================="
