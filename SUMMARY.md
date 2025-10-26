# Kaleido axref Bug: Investigation Summary

## The Bug

**Symptom:** `axref="x"` annotations fail with plotly 6.x
**Error:** `KaleidoError: Error 525: Cannot read properties of undefined (reading 'val')`
**Impact:** Any plot using data-coordinate annotation positioning breaks

## Root Cause

1. **Plotly 6.x** changed how it serializes figures
2. **Kaleido's `toImage()` shortcut** (used for plotly >= 1.30.0) skips full axis initialization
3. **Missing `.val` property** in axis autorange breaks coordinate transformations
4. **Result:** plotly.js can't convert data coordinates to pixels for arrow positioning

## Test Matrix Results

| Plotly | Kaleido | Result | Status |
|--------|---------|--------|--------|
| 5.24.1 | 0.2.1 | ✅ Pass | Works (plotly 5.x compatible) |
| 6.3.1 | 0.2.1 | ❌ Fail | Broken (demonstrates bug) |
| 6.3.1 | 1.x | ❌ Fail | Broken (demonstrates bug) |
| 6.3.1 | 1.x (patched) | ✅ Pass | **Fixed!** |

## The Fix

**Location:** `src/js/src/plotly/render.js` (lines 118-155)

**Change:** Always use `newPlot()` + `toImage()` approach for plotly >= 1.11.0

**Why it works:**
- Creates graph div with full initialization
- Sets up all axis properties including autorange
- Enables proper coordinate transformations

**Performance:** Negligible (this was the approach for plotly < 1.30.0)

## Repository Contents

This repo provides everything needed to demonstrate and fix the bug:

### Test Scripts
- **kaleido_axref_repro.py** - 20-line minimal reproduction
- **test_notebook_axref.py** - Real-world example from production notebook
- **test_matrix.py** - Comprehensive version testing

### GitHub Actions
- **.github/workflows/test.yml** - Automated testing matrix
- Runs on every push
- Demonstrates bug with plotly 6.x
- Verifies fix with patched kaleido

### Documentation
- **README.md** - Main documentation (start here)
- **NEXT_STEPS.md** - Step-by-step guide for filing issue
- **FORK_SETUP.md** - How to create kaleido fork
- **PATCHING_KALEIDO.md** - Technical patch details
- **KALEIDO_BUG_REPORT.md** - Original investigation notes
- **SUMMARY.md** - This file

## Quick Start

### Reproduce the Bug

```bash
pip install plotly==6.3.1 kaleido==0.2.1
python kaleido_axref_repro.py
# ❌ Fails with "Cannot read properties of undefined (reading 'val')"
```

### Test the Fix

```bash
pip install plotly==6.3.1
pip install git+https://github.com/YOUR_USERNAME/kaleido.git@axref-fix#subdirectory=src/py
python kaleido_axref_repro.py
# ✅ Success!
```

## Next Steps

See **NEXT_STEPS.md** for detailed instructions on:

1. Creating kaleido fork
2. Pushing fix branch
3. Creating bug report repo on GitHub
4. Filing issue with plotly/Kaleido
5. Creating pull request

## Key Files to Update

Before publishing, replace `YOUR_USERNAME` in:
- README.md
- .github/workflows/test.yml
- requirements.txt
- FORK_SETUP.md
- PATCHING_KALEIDO.md

## Timeline

1. **Original problem:** Production notebook using `axref="x"` broke after upgrading to plotly 6.x
2. **Initial hypothesis:** Kaleido 1.x introduced regression
3. **Discovery:** Both kaleido 0.2.1 AND 1.x fail with plotly 6.x
4. **Root cause:** Plotly 6.x serialization change + kaleido `toImage()` shortcut
5. **Fix:** Revert to `newPlot()` approach for all plotly versions
6. **Verification:** Fix tested and confirmed working

## Credits

Investigation and fix: @runsascoded with Claude Code
Reproduction: This repository
Fix location: https://github.com/YOUR_USERNAME/kaleido/tree/axref-fix
