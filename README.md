# Kaleido `axref="x"` Bug Reproduction

[![Test kaleido axref bug](https://github.com/YOUR_USERNAME/kaleido-axref-bug/actions/workflows/test.yml/badge.svg)](https://github.com/YOUR_USERNAME/kaleido-axref-bug/actions/workflows/test.yml)

This repository demonstrates and provides a fix for a critical bug in kaleido when using plotly 6.x with `axref="x"` annotations.

## The Bug

When using plotly 6.x with kaleido (any version), annotations using `axref="x"` or `ayref="y"` fail with:

```
KaleidoError: Error 525: Cannot read properties of undefined (reading 'val')
```

This breaks any plot that positions annotation arrows using data coordinates rather than pixel offsets.

## Reproduction

### Quick Test

```bash
python kaleido_axref_repro.py
```

### Test Matrix

The GitHub Actions workflow tests all combinations:

| Plotly | Kaleido | Result | Explanation |
|--------|---------|--------|-------------|
| 5.24.1 | 0.2.1 | ✅ Pass | Works fine with plotly 5.x |
| 6.3.1 | 0.2.1 | ❌ Fail | Plotly 6.x breaks with any kaleido |
| 6.3.1 | 1.x | ❌ Fail | Same error with kaleido 1.x |
| 6.3.1 | patched | ✅ Pass | Fix works! |

## Root Cause

Plotly 6.x changed how it serializes figures. Kaleido's `toImage()` shortcut (used for plotly >= 1.30.0) skips full axis initialization, which worked fine with plotly 5.x but breaks with 6.x.

Specifically, the shortcut doesn't initialize axis autorange properties (including `.val`), which plotly.js needs to convert data coordinates to pixels for arrow positioning.

## The Fix

**File:** `src/js/src/plotly/render.js` (lines 118-155)

Replace the direct `toImage()` shortcut with the full `newPlot()` + `toImage()` approach for all plotly versions >= 1.11.0:

```javascript
// Fix for axref="x" annotation bug with plotly 6.x
// The direct toImage() shortcut skips axis initialization needed for data-coordinate arrow positioning
if (semver.gte(Plotly.version, '1.11.0')) {
    const gd = document.createElement('div')

    promise = Plotly
      .newPlot(gd, figure.data, figure.layout, config)
      .then(() => Plotly.toImage(gd, imgOpts))
      .then((imgData) => {
        Plotly.purge(gd)
        // ... rest of processing
      })
}
```

### Why This Works

The `newPlot()` call:
1. Creates a graph div
2. Runs full plotly.js initialization
3. Sets up axis ranges and autorange properties (including `.val`)
4. Initializes coordinate transformations (`ax.r2p()` and friends)

This is what kaleido did for plotly < 1.30.0, and what it needs to do for plotly 6.x.

## Testing the Fix

### Local Testing

```bash
# Install patched kaleido from fork
pip install git+https://github.com/YOUR_USERNAME/kaleido.git@axref-fix#subdirectory=src/py

# Test with plotly 6.x
pip install plotly==6.3.1
python kaleido_axref_repro.py
```

Expected output:
```
✓ SUCCESS: Image saved to tmp/test_axref.png
  This means axref='x' works with your kaleido version
```

### GitHub Actions

The workflow automatically tests all combinations. See [Actions](https://github.com/YOUR_USERNAME/kaleido-axref-bug/actions) for results.

## Files

- `kaleido_axref_repro.py` - Minimal reproduction script
- `test_notebook_axref.py` - Real-world example from actual notebook
- `test_matrix.py` - Comprehensive test matrix (all version combinations)
- `.github/workflows/test.yml` - GitHub Actions workflow
- `KALEIDO_BUG_REPORT.md` - Detailed investigation notes

## Impact

This affects anyone using:
- Plotly 6.x for figure creation
- Kaleido for static image export
- Annotations with data-coordinate positioning (`axref`, `ayref`)

## Workarounds

### Option 1: Downgrade to plotly 5.x

```bash
pip install "plotly<6"
```

### Option 2: Use pixel offsets (BROKEN - doesn't position arrows correctly)

```python
# This "workaround" doesn't actually work properly
fig.add_annotation(
    x=x, y=y,
    ax=0, ay=-40,  # Pixel offsets instead of data coordinates
    text="annotation"
)
```

### Option 3: Use the patched kaleido (RECOMMENDED)

```bash
pip install git+https://github.com/YOUR_USERNAME/kaleido.git@axref-fix#subdirectory=src/py
```

## Performance Impact

Minimal. The `newPlot()` approach creates a temporary DOM element and runs full initialization, adding negligible overhead. This is what kaleido did for plotly < 1.30.0 anyway.

## Related Issues

- [plotly/Kaleido#XXX](https://github.com/plotly/Kaleido/issues/XXX) - Original issue report
- [plotly/plotly.py#XXXX](https://github.com/plotly/plotly.py/issues/XXXX) - Plotly.py side

## Contributing

1. Fork this repo to verify the bug in your environment
2. Test the fix
3. Report results in the issue thread

## License

MIT

## Acknowledgments

Investigation and fix by [@runsascoded](https://github.com/runsascoded) with assistance from Claude Code.
