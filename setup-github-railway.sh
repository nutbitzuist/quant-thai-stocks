#!/bin/bash

# Setup script for GitHub and Railway deployment

echo "🚀 Setting up GitHub and Railway deployment..."
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "📦 Installing Railway CLI..."
    if command -v npm &> /dev/null; then
        npm install -g @railway/cli
    elif command -v brew &> /dev/null; then
        brew install railway
    else
        echo "❌ Please install Railway CLI manually:"
        echo "   npm install -g @railway/cli"
        echo "   or"
        echo "   brew install railway"
        exit 1
    fi
else
    echo "✅ Railway CLI is already installed"
fi

echo ""
echo "📝 Next steps:"
echo ""
echo "1. Create GitHub repository:"
echo "   - Go to: https://github.com/new"
echo "   - Repository name: quant-thai-stocks (or your choice)"
echo "   - DO NOT initialize with README, .gitignore, or license"
echo "   - Click 'Create repository'"
echo ""
echo "2. Push to GitHub:"
echo "   git add ."
echo "   git commit -m 'Initial commit: Quant Stock Analysis Platform'"
echo "   git remote add origin https://github.com/YOUR_USERNAME/quant-thai-stocks.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3. Login to Railway:"
echo "   railway login"
echo ""
echo "4. Deploy Backend:"
echo "   cd backend"
echo "   railway init"
echo "   railway variables set DEBUG=false"
echo "   railway variables set CORS_ORIGINS='[\"*\"]'"
echo "   railway up"
echo ""
echo "5. Deploy Frontend:"
echo "   cd ../frontend"
echo "   railway link"
echo "   railway variables set NEXT_PUBLIC_API_URL=https://your-backend.up.railway.app"
echo "   railway up"
echo ""
echo "📖 For detailed instructions, see: RAILWAY_BOTH_DEPLOY.md"
echo ""

