#!/bin/bash
# Sync production database to test database on Render
# Run this script periodically to update test data from production

set -e  # Exit on error

echo "🔄 Production to Test Database Sync"
echo "===================================="
echo ""

# Check if DATABASE_URL environment variables are set
if [ -z "$PRODUCTION_DATABASE_URL" ]; then
    echo "❌ Error: PRODUCTION_DATABASE_URL not set"
    echo ""
    echo "Set it with:"
    echo "  export PRODUCTION_DATABASE_URL='postgresql://user:pass@host:port/dbname'"
    exit 1
fi

if [ -z "$TEST_DATABASE_URL" ]; then
    echo "❌ Error: TEST_DATABASE_URL not set"
    echo ""
    echo "Set it with:"
    echo "  export TEST_DATABASE_URL='postgresql://user:pass@host:port/dbname'"
    exit 1
fi

echo "📊 Source: Production Database"
echo "📥 Target: Test Database"
echo ""
echo "⚠️  WARNING: This will DELETE all data in the test database!"
read -p "Continue? (yes/no): " -r
echo ""

if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "❌ Aborted"
    exit 1
fi

echo "🔄 Starting sync..."
echo ""

# Create temporary dump file
DUMP_FILE="/tmp/production_backup_$(date +%Y%m%d_%H%M%S).sql"

echo "1️⃣  Dumping production database..."
pg_dump "$PRODUCTION_DATABASE_URL" --clean --no-owner --no-acl > "$DUMP_FILE"

if [ $? -eq 0 ]; then
    echo "✅ Production dump complete"
else
    echo "❌ Production dump failed"
    rm -f "$DUMP_FILE"
    exit 1
fi

echo ""
echo "2️⃣  Restoring to test database..."
psql "$TEST_DATABASE_URL" < "$DUMP_FILE"

if [ $? -eq 0 ]; then
    echo "✅ Test database restored"
else
    echo "❌ Test database restore failed"
    rm -f "$DUMP_FILE"
    exit 1
fi

# Clean up
rm -f "$DUMP_FILE"

echo ""
echo "✅ Sync complete!"
echo ""
echo "📊 Test database now has a copy of production data"
echo "🕒 Synced at: $(date)"
