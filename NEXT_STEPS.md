# Next Steps for Filing Kaleido Bug Report

## What We've Built

### 1. Bug Reproduction Repository (`/Users/ryan/c/hccs/path/kaleido-bug`)

This repo demonstrates the bug with comprehensive testing:

**Test Scripts:**
- `kaleido_axref_repro.py` - Minimal 10-line reproduction
- `test_notebook_axref.py` - Real-world example from actual notebook
- `test_matrix.py` - Tests all version combinations
- `test_lines.py` - Additional test case

**Documentation:**
- `README.md` - Main documentation with bug description, fix, and usage
- `KALEIDO_BUG_REPORT.md` - Detailed investigation notes (existing)
- `PATCHING_KALEIDO.md` - How to apply and test the patch
- `FORK_SETUP.md` - Step-by-step guide for creating fork and filing issue
- `requirements.txt` - Package requirements

**GitHub Actions:**
- `.github/workflows/test.yml` - Automated testing of all combinations
  - ✅ plotly 5.x + kaleido 0.2.1 (works)
  - ❌ plotly 6.x + kaleido 0.2.1 (fails - demonstrates bug)
  - ❌ plotly 6.x + kaleido 1.x (fails - demonstrates bug)
  - ✅ plotly 6.x + patched kaleido (works - demonstrates fix)

### 2. Patched Kaleido (`/Users/ryan/c/kaleido`)

The fix is already applied locally:

**Modified Files:**
- `src/js/src/plotly/render.js` - Core fix (lines 118-155)
- `src/py/kaleido/vendor/kaleido_scopes.js` - Rebuilt JavaScript bundle

**Status:** Ready to commit and push to fork

## Required Actions

### Step 1: Create Kaleido Fork

```bash
# On GitHub:
# 1. Go to https://github.com/plotly/Kaleido
# 2. Click "Fork"
# 3. Fork to your account

# Then locally:
cd /Users/ryan/c/kaleido
git remote add ryan-williams https://github.com/ryan-williams/kaleido.git
```

### Step 2: Push Fix Branch

```bash
cd /Users/ryan/c/kaleido

# Create branch
git checkout -b axref-fix

# Add changes
git add src/js/src/plotly/render.js
git add src/py/kaleido/vendor/kaleido_scopes.js

# Commit (detailed message in FORK_SETUP.md)
git commit -F- <<'EOF'
Fix axref='x' annotations with plotly 6.x

The direct toImage() shortcut (used for plotly >= 1.30.0) breaks with
plotly 6.x when using axref='x' or ayref='y' for data-coordinate
annotation positioning.

Root cause: Plotly 6.x changed figure serialization. The toImage()
shortcut skips axis initialization, specifically the autorange
properties that include .val, which plotly.js needs for coordinate
transformations.

This fix always uses newPlot() + toImage() approach for plotly >= 1.11.0,
ensuring full axis initialization.

Error fixed: Cannot read properties of undefined (reading 'val')

Tested with:
- plotly 5.24.1 + kaleido 0.2.1: ✅ Works (unchanged)
- plotly 6.3.1 + kaleido 0.2.1: ❌ Fails (demonstrates bug)
- plotly 6.3.1 + kaleido 1.x (original): ❌ Fails (demonstrates bug)
- plotly 6.3.1 + kaleido 1.x (patched): ✅ Works (fix verified)
EOF

# Push to your fork
git push ryan-williams axref-fix
```

### Step 3: Update Bug Report Repo URLs

```bash
cd /Users/ryan/c/hccs/path/kaleido-bug

# Replace ryan-williams with your GitHub username in:
# - README.md (multiple locations)
# - .github/workflows/test.yml
# - requirements.txt
# - FORK_SETUP.md
# - PATCHING_KALEIDO.md
```

### Step 4: Create Bug Report Repo on GitHub

```bash
cd /Users/ryan/c/hccs/path/kaleido-bug

# Create repo on GitHub first, then:
git remote add origin https://github.com/ryan-williams/kaleido-axref-bug.git

# Review what will be committed
git status

# Add all files
git add .

# Commit
git commit -m "Initial commit: kaleido axref bug reproduction and fix

Demonstrates plotly 6.x regression with axref annotations.

Includes:
- Minimal reproduction script
- Real-world notebook example
- GitHub Actions test matrix
- Comprehensive documentation
- Link to patched kaleido fork

See README.md for full details.
"

# Push
git push -u origin main
```

### Step 5: Verify GitHub Actions

1. Go to https://github.com/ryan-williams/kaleido-axref-bug/actions
2. Verify workflows run automatically
3. Check that tests demonstrate the bug and fix

Expected results:
- ✅ plotly 5.x + kaleido 0.2.1: Pass (works as expected)
- ❌ plotly 6.x + kaleido 0.2.1: Fail (demonstrates bug)
- ❌ plotly 6.x + kaleido 1.x: Fail (demonstrates bug)
- ✅ plotly 6.x + patched kaleido: Pass (demonstrates fix)

### Step 6: File GitHub Issue

File at: https://github.com/plotly/Kaleido/issues/new

**Title:**
```
`axref="x"` annotations fail with plotly 6.x: "Cannot read properties of undefined (reading 'val')"
```

**Body template in FORK_SETUP.md** - includes:
- Bug description
- Link to reproduction repo
- Minimal code example
- Test results
- Root cause analysis
- Link to fix

### Step 7: Create Pull Request (Optional but Recommended)

After issue is filed:

1. Go to https://github.com/plotly/Kaleido/compare
2. Select: `base: master` ← `compare: ryan-williams:axref-fix`
3. Create PR with:
   - Reference to issue number
   - Link to reproduction/test repo
   - Explanation of fix

## Testing Locally Before Publishing

### Test the Bug Reproduction

```bash
cd /Users/ryan/c/hccs/path/kaleido-bug

# Test with plotly 5.x (should work)
pip install plotly==5.24.1 kaleido==0.2.1
python kaleido_axref_repro.py
# Expected: ✅ SUCCESS

# Test with plotly 6.x (should fail, demonstrating bug)
pip install plotly==6.3.1 kaleido==0.2.1
python kaleido_axref_repro.py
# Expected: ❌ FAIL with "Cannot read properties of undefined (reading 'val')"

# Test with patched kaleido (should work)
pip install -e /Users/ryan/c/kaleido/src/py
python kaleido_axref_repro.py
# Expected: ✅ SUCCESS
```

### Test GitHub Actions Locally

```bash
cd /Users/ryan/c/hccs/path/kaleido-bug

# Install act (GitHub Actions local runner)
brew install act

# Run workflows locally
act
```

## Repository Structure

```
kaleido-axref-bug/
├── .github/
│   └── workflows/
│       └── test.yml                 # GitHub Actions workflow
├── .gitignore                       # Ignore test outputs
├── README.md                        # Main documentation
├── KALEIDO_BUG_REPORT.md           # Detailed investigation
├── PATCHING_KALEIDO.md             # Patch instructions
├── FORK_SETUP.md                   # Fork and issue filing guide
├── NEXT_STEPS.md                   # This file
├── requirements.txt                # Package requirements
├── kaleido_axref_repro.py          # Minimal reproduction
├── test_notebook_axref.py          # Real-world example
└── test_matrix.py                  # Comprehensive test matrix
```

## Quick Reference

**Bug:**
- `axref="x"` annotations fail with plotly 6.x
- Error: "Cannot read properties of undefined (reading 'val')"
- Affects ALL kaleido versions when using plotly 6.x

**Root Cause:**
- Plotly 6.x changed figure serialization
- Kaleido's `toImage()` shortcut skips axis initialization
- Missing `.val` property breaks coordinate transformations

**Fix:**
- Always use `newPlot()` + `toImage()` for full initialization
- File: `src/js/src/plotly/render.js` (lines 118-155)
- Performance impact: Minimal (this was the pre-1.30.0 approach anyway)

**Status:**
- ✅ Bug reproduced
- ✅ Root cause identified
- ✅ Fix implemented and tested
- ✅ Documentation complete
- ⏳ Awaiting fork creation and issue filing
