#!/bin/bash

# Version Bump Script
# Usage: ./bump-version.sh [major|minor|patch]
# Example: ./bump-version.sh patch  (2.0.0 -> 2.0.1)

set -e

VERSION_FILE="VERSION"
FRONTEND_PACKAGE="frontend/package.json"
BACKEND_MAIN="backend/app/main.py"
FRONTEND_PAGE="frontend/src/app/page.tsx"

if [ ! -f "$VERSION_FILE" ]; then
    echo "Creating VERSION file..."
    echo "2.0.0" > "$VERSION_FILE"
fi

CURRENT_VERSION=$(cat "$VERSION_FILE")
echo "Current version: $CURRENT_VERSION"

# Parse version
IFS='.' read -ra VERSION_PARTS <<< "$CURRENT_VERSION"
MAJOR=${VERSION_PARTS[0]}
MINOR=${VERSION_PARTS[1]}
PATCH=${VERSION_PARTS[2]}

# Determine bump type
BUMP_TYPE=${1:-patch}

case $BUMP_TYPE in
    major)
        MAJOR=$((MAJOR + 1))
        MINOR=0
        PATCH=0
        ;;
    minor)
        MINOR=$((MINOR + 1))
        PATCH=0
        ;;
    patch)
        PATCH=$((PATCH + 1))
        ;;
    *)
        echo "Usage: $0 [major|minor|patch]"
        exit 1
        ;;
esac

NEW_VERSION="$MAJOR.$MINOR.$PATCH"
echo "New version: $NEW_VERSION"

# Update VERSION file
echo "$NEW_VERSION" > "$VERSION_FILE"

# Update frontend package.json
if [ -f "$FRONTEND_PACKAGE" ]; then
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/\"version\": \".*\"/\"version\": \"$NEW_VERSION\"/" "$FRONTEND_PACKAGE"
    else
        # Linux
        sed -i "s/\"version\": \".*\"/\"version\": \"$NEW_VERSION\"/" "$FRONTEND_PACKAGE"
    fi
    echo "✓ Updated $FRONTEND_PACKAGE"
fi

# Update backend main.py (2 places)
if [ -f "$BACKEND_MAIN" ]; then
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/version=\"[^\"]*\"/version=\"$NEW_VERSION\"/g" "$BACKEND_MAIN"
        sed -i '' "s/\"version\": \"[^\"]*\"/\"version\": \"$NEW_VERSION\"/g" "$BACKEND_MAIN"
    else
        # Linux
        sed -i "s/version=\"[^\"]*\"/version=\"$NEW_VERSION\"/g" "$BACKEND_MAIN"
        sed -i "s/\"version\": \"[^\"]*\"/\"version\": \"$NEW_VERSION\"/g" "$BACKEND_MAIN"
    fi
    echo "✓ Updated $BACKEND_MAIN"
fi

# Update frontend page.tsx (header title)
if [ -f "$FRONTEND_PAGE" ]; then
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/Quant Stock Analysis v[0-9.]*/Quant Stock Analysis v$NEW_VERSION/g" "$FRONTEND_PAGE"
    else
        # Linux
        sed -i "s/Quant Stock Analysis v[0-9.]*/Quant Stock Analysis v$NEW_VERSION/g" "$FRONTEND_PAGE"
    fi
    echo "✓ Updated $FRONTEND_PAGE"
fi

echo ""
echo "✅ Version bumped to $NEW_VERSION"
echo ""
echo "Next steps:"
echo "  git add VERSION $FRONTEND_PACKAGE $BACKEND_MAIN $FRONTEND_PAGE"
echo "  git commit -m \"Bump version to $NEW_VERSION\""
echo "  git push"

