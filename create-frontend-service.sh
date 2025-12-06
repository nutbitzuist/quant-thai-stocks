#!/bin/bash
# Create frontend service via Railway API

PROJECT_ID="a54028cf-667f-4889-989c-7574b61ae6e4"
SERVICE_NAME="frontend"

echo "Creating frontend service via Railway dashboard..."
echo ""
echo "Since Railway CLI doesn't support creating services directly,"
echo "please create it via the dashboard:"
echo ""
echo "1. Go to: https://railway.com/project/$PROJECT_ID"
echo "2. Click '+ New' → 'GitHub Repo'"
echo "3. Select: nutbitzuist/quant-thai-stocks"
echo "4. Set Root Directory: frontend"
echo "5. Click 'Deploy'"
echo ""
echo "Then run: cd frontend && railway service link frontend"
