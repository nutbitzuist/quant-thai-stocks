#!/bin/bash
# Deploy frontend to Railway - Automated script

echo "🚀 Deploying Frontend to Railway..."
echo ""

cd frontend

# Check if service exists, if not, create via API
PROJECT_ID="a54028cf-667f-4889-989c-7574b61ae6e4"

echo "Step 1: Setting environment variable..."
railway variables --set NEXT_PUBLIC_API_URL=https://quant-stocks-backend-production.up.railway.app 2>&1 || echo "Note: Set this manually in Railway dashboard"

echo ""
echo "Step 2: Deploying..."
echo "If service doesn't exist, Railway will prompt you to create it"
echo ""

# Try to deploy - this might fail if service doesn't exist
railway up --detach 2>&1

echo ""
echo "✅ If deployment failed, create the service first:"
echo "   1. Go to: https://railway.com/project/$PROJECT_ID"
echo "   2. Click '+ New' → 'GitHub Repo'"
echo "   3. Select: nutbitzuist/quant-thai-stocks"
echo "   4. Set Root Directory: frontend"
echo "   5. Then run this script again"
