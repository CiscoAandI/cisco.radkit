# GitHub Actions Documentation Workflows Configuration

This directory contains GitHub Actions workflows for building and deploying your Ansible collection documentation.

## Workflows

### 1. docs-build.yml
**Purpose**: Build documentation on pull requests and pushes to verify everything works correctly.

**Triggers**:
- Pull requests to main/master branches
- Pushes to main/master branches
- Manual workflow dispatch
- Changes to docs/, plugins/, meta/, or galaxy.yml

**What it does**:
- Installs Python and dependencies
- Installs your collection
- Runs the docs/build.sh script
- Uploads built documentation as artifacts
- Validates the build completed successfully

### 2. docs-deploy.yml
**Purpose**: Build and deploy documentation to GitHub Pages on pushes to main branch.

**Triggers**:
- Pushes to main/master branches
- Manual workflow dispatch
- Changes to docs/, plugins/, meta/, or galaxy.yml

**What it does**:
- Builds documentation using docs/build.sh
- Deploys to GitHub Pages
- Creates .nojekyll file for proper GitHub Pages rendering

**Setup Required**:
1. Go to your repository Settings → Pages
2. Set Source to "GitHub Actions"
3. The workflow will automatically deploy to https://yourusername.github.io/cisco.radkit

### 3. docs-quality.yml
**Purpose**: Check documentation quality and validate plugin documentation.

**Triggers**:
- Pull requests to main/master branches
- Manual workflow dispatch
- Changes to docs/, plugins/, or README.md

**What it does**:
- Checks RST syntax
- Validates documentation style with doc8
- Checks for broken links
- Validates galaxy.yml format
- Ensures all plugins have docstrings
- Generates documentation coverage report

## Configuration

### Environment Variables
You can customize the workflows by setting these in your repository secrets:

- `CUSTOM_DOMAIN`: If you have a custom domain for GitHub Pages

### Customization
To customize the workflows:

1. **Python Version**: Change `python-version: '3.11'` to your preferred version
2. **Build Command**: Modify the build steps if you need different build commands
3. **Deployment Branch**: Change `branches: [ main, master ]` to match your default branch
4. **File Paths**: Adjust the `paths:` filters to match your project structure

### Troubleshooting

#### Build Failures
- Check the "Upload build logs on failure" artifact for detailed error logs
- Ensure all dependencies in docs/requirements.txt are correct
- Verify your build.sh script works locally

#### Deployment Issues
- Ensure GitHub Pages is enabled in repository settings
- Check that the workflow has proper permissions (workflow should set these automatically)
- Verify the built HTML files are in the correct location

#### Quality Check Failures
- Fix RST syntax errors reported by the quality check
- Add missing docstrings to plugins
- Resolve broken links in documentation

## Manual Testing

To test locally before pushing:

```bash
# Test documentation build
cd docs
./build.sh

# Test quality checks
pip install doc8
doc8 docs/rst/ --max-line-length 100 --ignore D001

# Check for syntax errors
find docs/rst -name "*.rst" -exec python -m docutils.parsers.rst {} \;
```

## Next Steps

1. Push these workflows to your repository
2. Enable GitHub Pages in repository settings
3. Create a pull request to test the build workflow
4. Merge to main branch to test deployment workflow

The documentation will be available at: https://ciscoaandi.github.io/cisco.radkit
