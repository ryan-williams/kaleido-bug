# Setting Up Kaleido Fork for Bug Report

This documents the steps to create a GitHub fork and branch with the fix.

## Steps for Creating the Fork

### 1. Fork on GitHub

1. Go to https://github.com/plotly/Kaleido
2. Click "Fork" button
3. Create fork under your username

### 2. Add Your Fork as Remote

```bash
cd /Users/ryan/c/kaleido

# Add your fork as a remote (replace ryan-williams)
git remote add rw https://github.com/ryan-williams/kaleido.git

# Verify
git remote -v
```

### 3. Create and Push Fix Branch

```bash
# Create branch from current state (already has the fix applied)
git checkout -b axref-fix

# Add the changes
git add src/js/src/plotly/render.js
git add src/py/kaleido/vendor/kaleido_scopes.js

# Commit with detailed message
git commit -m "Fix axref='x' annotations with plotly 6.x

The direct toImage() shortcut (used for plotly >= 1.30.0) breaks with
plotly 6.x when using axref='x' or ayref='y' for data-coordinate
annotation positioning.

Root cause: Plotly 6.x changed figure serialization. The toImage()
shortcut skips axis initialization, specifically the autorange
properties that include .val, which plotly.js needs for coordinate
transformations.

This fix always uses newPlot() + toImage() approach for plotly >= 1.11.0,
ensuring full axis initialization. This was the approach used for
plotly < 1.30.0, and is what's needed for plotly 6.x compatibility.

Error fixed: Cannot read properties of undefined (reading 'val')

Tested with:
- plotly 5.24.1 + kaleido 0.2.1: ✅ Works (unchanged)
- plotly 6.3.1 + kaleido 0.2.1: ❌ Fails (demonstrates bug)
- plotly 6.3.1 + kaleido 1.x (original): ❌ Fails (demonstrates bug)
- plotly 6.3.1 + kaleido 1.x (patched): ✅ Works (fix verified)

Reproduction: https://github.com/ryan-williams/kaleido-axref-bug
"

# Push to your fork
git push rw axref-fix
```

### 4. Update Bug Report Repo

Once the fork branch is pushed, update these files in `/Users/ryan/c/hccs/path/kaleido-bug`:

**README.md:**
- Replace `ryan-williams` with actual GitHub username
- Update badge URL
- Update fork installation command

**.github/workflows/test.yml:**
- Replace `ryan-williams` in the patched kaleido installation URL

**requirements.txt:**
- Update the fork URL

### 5. Test Fork Installation

```bash
# Create fresh test environment
python -m venv /tmp/test-kaleido-fork
source /tmp/test-kaleido-fork/bin/activate

# Install from fork
pip install pandas plotly==6.3.1
pip install git+https://github.com/ryan-williams/kaleido.git@axref-fix#subdirectory=src/py

# Test
cd /Users/ryan/c/hccs/path/kaleido-bug
python kaleido_axref_repro.py
```

Expected output:
```
✓ SUCCESS: Image saved to tmp/test_axref.png
```

### 6. Push Bug Report Repo

```bash
cd /Users/ryan/c/hccs/path/kaleido-bug

# Stage all files
git add .

# Commit
git commit -m "Initial commit: kaleido axref bug reproduction

Demonstrates plotly 6.x regression with axref annotations and provides fix.

Includes:
- Minimal reproduction script
- Real-world notebook example
- GitHub Actions test matrix
- Comprehensive documentation
- Link to patched kaleido fork
"

# Create repo on GitHub, then:
git remote add origin https://github.com/ryan-williams/kaleido-axref-bug.git
git push -u origin main
```

### 7. Create GitHub Issue

File issue at https://github.com/plotly/Kaleido/issues/new with:

**Title:** `axref="x"` annotations fail with plotly 6.x: "Cannot read properties of undefined (reading 'val')"

**Body:**
```markdown
## Bug Description

Annotations using `axref="x"` or `ayref="y"` for data-coordinate positioning fail with plotly 6.x:

\`\`\`
KaleidoError: Error 525: Cannot read properties of undefined (reading 'val')
\`\`\`

## Reproduction

Full reproduction with test matrix: https://github.com/ryan-williams/kaleido-axref-bug

Minimal example:
\`\`\`python
import pandas as pd
import plotly.express as px

data = pd.DataFrame({'Value': [100, 200, 300]},
                   index=pd.date_range('2012-01', periods=3, freq='MS'))
fig = px.line(data)
idx = data.index.to_series()

fig.add_annotation(
    x=idx.iloc[-1],
    ax=idx.iloc[-2],
    axref="x",  # ← This breaks
    y=300, ay=350,
    text="Test"
)

fig.write_image('test.png')  # Fails
\`\`\`

## Versions Affected

- ❌ kaleido 0.2.1 + plotly 6.x
- ❌ kaleido 1.x + plotly 6.x
- ✅ kaleido 0.2.1 + plotly 5.x (works)

## Root Cause

Plotly 6.x changed figure serialization. Kaleido's `toImage()` shortcut (used for plotly >= 1.30.0) skips axis initialization, specifically autorange properties including `.val`.

## Fix

Always use `newPlot()` + `toImage()` for full axis initialization.

Patched version: https://github.com/ryan-williams/kaleido/tree/axref-fix

Fix confirmed working: https://github.com/ryan-williams/kaleido-axref-bug/actions

## Installation

\`\`\`bash
pip install git+https://github.com/ryan-williams/kaleido.git@axref-fix#subdirectory=src/py
\`\`\`
```

## Summary

After completing these steps, you'll have:

1. ✅ Kaleido fork with fix on `axref-fix` branch
2. ✅ Bug reproduction repo with GitHub Actions
3. ✅ Comprehensive documentation
4. ✅ GitHub issue filed with working fix

The GitHub Actions in the bug report repo will automatically demonstrate:
- The bug exists with plotly 6.x
- The bug doesn't exist with plotly 5.x
- The fix works with plotly 6.x
