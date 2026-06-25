#!/bin/bash

# Quick PostgreSQL Setup Script for Docker
# =========================================
# This script sets up a PostgreSQL database in Docker for local development

set -e

echo "🚀 Setting up PostgreSQL database for RealDiag..."
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
CONTAINER_NAME="realdiag-postgres"
DB_NAME="realdiag_dev"
DB_USER="realdiag_user"
DB_PASSWORD="devpassword123"
DB_PORT="5432"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed!${NC}"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if container already exists
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${YELLOW}⚠️  Container '${CONTAINER_NAME}' already exists${NC}"
    read -p "Do you want to remove it and create a new one? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  Removing existing container..."
        docker rm -f ${CONTAINER_NAME}
    else
        echo "Keeping existing container. Starting it..."
        docker start ${CONTAINER_NAME}
        echo -e "${GREEN}✅ Database is running!${NC}"
        echo ""
        echo "Database URL:"
        echo "postgresql://${DB_USER}:${DB_PASSWORD}@localhost:${DB_PORT}/${DB_NAME}"
        exit 0
    fi
fi

# Pull PostgreSQL image
echo "📦 Pulling PostgreSQL 16 image..."
docker pull postgres:16-alpine

# Run PostgreSQL container
echo "🐘 Starting PostgreSQL container..."
docker run -d \
  --name ${CONTAINER_NAME} \
  -e POSTGRES_DB=${DB_NAME} \
  -e POSTGRES_USER=${DB_USER} \
  -e POSTGRES_PASSWORD=${DB_PASSWORD} \
  -p ${DB_PORT}:5432 \
  --health-cmd="pg_isready -U ${DB_USER}" \
  --health-interval=5s \
  --health-timeout=3s \
  --health-retries=5 \
  postgres:16-alpine

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 5

# Check if container is running
if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${GREEN}✅ PostgreSQL is running!${NC}"
else
    echo -e "${RED}❌ Failed to start PostgreSQL${NC}"
    echo "Check logs with: docker logs ${CONTAINER_NAME}"
    exit 1
fi

# Create DATABASE_URL
DATABASE_URL="postgresql://${DB_USER}:${DB_PASSWORD}@localhost:${DB_PORT}/${DB_NAME}"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}🎉 PostgreSQL Database Setup Complete!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Database Details:"
echo "  Container: ${CONTAINER_NAME}"
echo "  Database:  ${DB_NAME}"
echo "  User:      ${DB_USER}"
echo "  Password:  ${DB_PASSWORD}"
echo "  Port:      ${DB_PORT}"
echo ""
echo "Database URL:"
echo -e "${YELLOW}${DATABASE_URL}${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Next Steps:"
echo ""
echo "1. Set the DATABASE_URL environment variable:"
echo "   ${GREEN}export DATABASE_URL=\"${DATABASE_URL}\"${NC}"
echo ""
echo "2. Or add it to your backend/.env file:"
echo "   ${GREEN}echo 'DATABASE_URL=\"${DATABASE_URL}\"' >> backend/.env${NC}"
echo ""
echo "3. Start your backend:"
echo "   ${GREEN}cd backend && python main.py${NC}"
echo ""
echo "Useful Commands:"
echo "  Stop database:    ${GREEN}docker stop ${CONTAINER_NAME}${NC}"
echo "  Start database:   ${GREEN}docker start ${CONTAINER_NAME}${NC}"
echo "  View logs:        ${GREEN}docker logs ${CONTAINER_NAME}${NC}"
echo "  Connect to psql:  ${GREEN}docker exec -it ${CONTAINER_NAME} psql -U ${DB_USER} -d ${DB_NAME}${NC}"
echo "  Remove database:  ${GREEN}docker rm -f ${CONTAINER_NAME}${NC}"
echo ""

# Offer to set the environment variable
read -p "Do you want to export DATABASE_URL to your current shell? (Y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    export DATABASE_URL="${DATABASE_URL}"
    echo -e "${GREEN}✅ DATABASE_URL exported!${NC}"
    echo ""
    echo "You can now start your backend with:"
    echo "  cd backend && python main.py"
else
    echo ""
    echo "Remember to set DATABASE_URL before starting the backend:"
    echo "  export DATABASE_URL=\"${DATABASE_URL}\""
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
