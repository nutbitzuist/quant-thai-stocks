#!/bin/bash

# Script to commit and push all changes to GitHub
# This ensures Railway auto-deploys on every change

echo "🚀 Pushing changes to GitHub for auto-deployment..."
echo ""

# Check if there are changes
if [ -z "$(git status --porcelain)" ]; then
    echo "✅ No changes to commit"
    exit 0
fi

# Show what will be committed
echo "📋 Changes to commit:"
git status --short
echo ""

# Ask for commit message
if [ -z "$1" ]; then
    read -p "Enter commit message (or press Enter for default): " COMMIT_MSG
    if [ -z "$COMMIT_MSG" ]; then
        COMMIT_MSG="Update: $(date '+%Y-%m-%d %H:%M:%S')"
    fi
else
    COMMIT_MSG="$1"
fi

# Add all changes
echo "📦 Adding changes..."
git add -A

# Commit
echo "💾 Committing: $COMMIT_MSG"
git commit -m "$COMMIT_MSG"

# Push
echo "⬆️  Pushing to GitHub..."
git push

echo ""
echo "✅ Changes pushed! Railway will auto-deploy in 2-3 minutes"
echo "📊 Check deployment: https://railway.com/project/a54028cf-667f-4889-989c-7574b61ae6e4"

