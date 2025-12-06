# Version Management Guide

## Automatic Version Bumping

This project now has an automatic version bumping system that updates version numbers across all files.

## How to Use

### Bump Version via CLI

```bash
# Bump patch version (2.0.0 -> 2.0.1)
./bump-version.sh patch

# Bump minor version (2.0.0 -> 2.1.0)
./bump-version.sh minor

# Bump major version (2.0.0 -> 3.0.0)
./bump-version.sh major
```

### What Gets Updated

The script automatically updates:
1. **VERSION** file (root directory)
2. **frontend/package.json** - version field
3. **backend/app/main.py** - FastAPI version and health check version
4. **frontend/src/app/page.tsx** - Header title version

### Workflow

1. Make your code changes
2. Bump the version:
   ```bash
   ./bump-version.sh patch
   ```
3. Commit everything:
   ```bash
   git add .
   git commit -m "Your changes - bump version to X.X.X"
   git push
   ```

## Version Number Format

Uses [Semantic Versioning](https://semver.org/):
- **MAJOR.MINOR.PATCH** (e.g., 2.0.1)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

## Current Version

Check the current version:
```bash
cat VERSION
```

Or check in the app:
- Frontend header: "📈 Quant Stock Analysis v2.0.2"
- Backend API: `/health` endpoint shows version
- Frontend package.json: `"version": "2.0.2"`

## Manual Version Update

If you need to set a specific version manually:

1. Edit `VERSION` file:
   ```bash
   echo "2.1.0" > VERSION
   ```

2. Run the bump script (it will sync all files):
   ```bash
   ./bump-version.sh patch  # This will read from VERSION and sync
   ```

## Integration with Git

The version bump script is designed to work with git:

```bash
# Complete workflow
./bump-version.sh patch
git add VERSION frontend/package.json backend/app/main.py frontend/src/app/page.tsx
git commit -m "Bump version to $(cat VERSION)"
git push
```

## Notes

- The script works on both macOS and Linux
- Version is stored in a single `VERSION` file for easy reference
- All version references are kept in sync automatically
- The script shows what files were updated

