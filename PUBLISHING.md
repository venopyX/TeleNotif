# Publishing Guide

Guide for publishing new versions of Telegrify to PyPI.

## Prerequisites

1. PyPI account: https://pypi.org/account/register/
2. PyPI API token: https://pypi.org/manage/account/token/
3. Install build tools:
   ```bash
   pip install build twine
   ```

---

## Manual Publishing

### 1. Update Version

Update version in these 3 files:

```bash
# pyproject.toml
version = "X.Y.Z"

# telegrify/__version__.py
__version__ = "X.Y.Z"

# telegrify/cli/commands.py
@click.version_option(version="X.Y.Z")
```

### 2. Update CHANGELOG.md

Add entry for the new version:

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- New feature

### Fixed
- Bug fix

### Changed
- Change description
```

### 3. Commit Changes

```bash
git add -A
git commit -m "chore: bump version to X.Y.Z"
git tag vX.Y.Z
```

### 4. Build Package

```bash
# Clean previous builds
rm -rf dist/

# Build
python -m build
```

This creates:
- `dist/telegrify-X.Y.Z-py3-none-any.whl`
- `dist/telegrify-X.Y.Z.tar.gz`

### 5. Upload to PyPI

```bash
twine upload dist/*
```

When prompted:
- Username: `__token__`
- Password: `pypi-YOUR_API_TOKEN`

Or use environment variable:
```bash
TWINE_USERNAME=__token__ TWINE_PASSWORD=pypi-xxx twine upload dist/*
```

### 6. Push to GitHub with Tag and Release

```bash
# Push code
git push origin main

# Push tag (required - tags don't push automatically!)
git push origin vX.Y.Z

# Create GitHub release with artifacts
gh release create vX.Y.Z dist/* \
  --title "vX.Y.Z - Release Title" \
  --notes "Release notes here"
```

Or generate release notes automatically from commits:
```bash
gh release create vX.Y.Z dist/* --generate-notes
```

---

## GitHub Actions (Automated)

If GitHub Actions is enabled on your account, the workflow will automatically publish when you push a version tag.

### Setup Trusted Publishing (Recommended)

1. Go to https://pypi.org/manage/account/publishing/
2. Add pending publisher:
   - Project: `telegrify`
   - Owner: `venopyx`
   - Repository: `telegrify`
   - Workflow: `publish.yml`
   - Environment: `pypi`

3. Create GitHub environment:
   - Go to repo Settings → Environments
   - Create environment named `pypi`

### Publish with GitHub Actions

```bash
# Update version, commit, then:
git tag vX.Y.Z
git push origin main --tags
```

The workflow automatically:
1. Runs tests
2. Builds package
3. Publishes to PyPI
4. Creates GitHub release

---

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (X.0.0): Breaking changes
- **MINOR** (0.X.0): New features, backward compatible
- **PATCH** (0.0.X): Bug fixes, backward compatible

Examples:
- `0.9.0` → `0.9.1` (bug fix)
- `0.9.1` → `0.10.0` (new feature)
- `0.10.0` → `1.0.0` (stable release or breaking change)

---

## Quick Reference

```bash
# Full manual release process
vim pyproject.toml                    # Update version
vim telegrify/__version__.py          # Update version
vim telegrify/cli/commands.py         # Update version
vim CHANGELOG.md                      # Add changelog entry

git add -A
git commit -m "chore: bump version to X.Y.Z"
git tag -a vX.Y.Z -m "vX.Y.Z - Release title"

rm -rf dist/
python -m build
twine upload dist/*

git push origin main
git push origin vX.Y.Z
gh release create vX.Y.Z dist/* --title "vX.Y.Z - Title" --generate-notes
```

---

## Troubleshooting

### "File already exists" error
You cannot overwrite an existing version on PyPI. Bump the version number.

### "Invalid token" error
- Ensure token starts with `pypi-`
- Check token hasn't expired
- Verify token has upload permissions

### Build fails
```bash
pip install --upgrade build poetry-core
```

### Test on TestPyPI first
```bash
twine upload --repository testpypi dist/*
pip install --index-url https://test.pypi.org/simple/ telegrify
```
