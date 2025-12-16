#!/bin/bash

# AI Content Enrichment Setup Script for RealDiag
# This script helps you configure AI-powered content generation

echo "🤖 RealDiag AI Content Enrichment Setup"
echo "========================================"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Creating .env file..."
    touch .env
fi

echo "AI content enrichment can generate missing clinical information"
echo "(treatment, clinical pearls, referrals, homeopathy) for diagnoses."
echo ""
echo "Choose your AI provider:"
echo "1) Claude (Anthropic) - Recommended for medical content"
echo "2) OpenAI GPT-4"
echo "3) Skip - Don't enable AI enrichment"
echo ""

read -p "Enter choice [1-3]: " choice

case $choice in
    1)
        echo ""
        echo "Selected: Claude (Anthropic)"
        echo "Get your API key from: https://console.anthropic.com/"
        echo ""
        read -p "Enter your Anthropic API key (or press Enter to skip): " api_key
        
        if [ -n "$api_key" ]; then
            # Remove existing keys
            sed -i '/^ANTHROPIC_API_KEY=/d' .env
            sed -i '/^OPENAI_API_KEY=/d' .env
            sed -i '/^AI_PROVIDER=/d' .env
            
            # Add new keys
            echo "" >> .env
            echo "# AI Content Enrichment" >> .env
            echo "ANTHROPIC_API_KEY=$api_key" >> .env
            echo "AI_PROVIDER=claude" >> .env
            
            echo ""
            echo "✅ Claude API key configured!"
            echo "   AI enrichment will automatically activate when the backend starts."
        else
            echo "Skipped API key setup."
        fi
        ;;
        
    2)
        echo ""
        echo "Selected: OpenAI GPT-4"
        echo "Get your API key from: https://platform.openai.com/api-keys"
        echo ""
        read -p "Enter your OpenAI API key (or press Enter to skip): " api_key
        
        if [ -n "$api_key" ]; then
            # Remove existing keys
            sed -i '/^ANTHROPIC_API_KEY=/d' .env
            sed -i '/^OPENAI_API_KEY=/d' .env
            sed -i '/^AI_PROVIDER=/d' .env
            
            # Add new keys
            echo "" >> .env
            echo "# AI Content Enrichment" >> .env
            echo "OPENAI_API_KEY=$api_key" >> .env
            echo "AI_PROVIDER=openai" >> .env
            
            echo ""
            echo "✅ OpenAI API key configured!"
            echo "   AI enrichment will automatically activate when the backend starts."
        else
            echo "Skipped API key setup."
        fi
        ;;
        
    3)
        echo ""
        echo "Skipping AI enrichment setup."
        echo "The diagnostic search will work normally without AI enrichment."
        ;;
        
    *)
        echo ""
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "📦 Installing required Python packages..."
pip install anthropic openai

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Restart your backend server to activate AI enrichment"
echo "2. Search for any diagnosis in the diagnostic search feature"
echo "3. Look for the 🤖 icon indicating AI-enriched content"
echo ""
echo "Documentation: See AI_CONTENT_ENRICHMENT.md for detailed information"
echo ""
