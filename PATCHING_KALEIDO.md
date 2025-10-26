# Patching Kaleido for axref Fix

This document explains how to fork kaleido, apply the patch, and publish it for testing.

## Quick Start

If you just want to use the patched version:

```bash
pip install git+https://github.com/YOUR_USERNAME/kaleido.git@axref-fix#subdirectory=src/py
```

## Creating the Fork and Patch

### 1. Fork Kaleido

```bash
# Fork plotly/Kaleido on GitHub to YOUR_USERNAME/kaleido
# Then clone your fork
cd /Users/ryan/c/kaleido  # Or wherever you want to work

# Add upstream remote
git remote add upstream https://github.com/plotly/Kaleido.git
```

### 2. Create Fix Branch

```bash
cd /Users/ryan/c/kaleido
git checkout -b axref-fix
```

### 3. Apply the Patch

The patch is already applied in `/Users/ryan/c/kaleido/src/js/src/plotly/render.js`.

**Changed file:** `src/js/src/plotly/render.js` (lines 118-155)

**Key change:** Always use `newPlot()` + `toImage()` for plotly >= 1.11.0, removing the direct `toImage()` shortcut that was used for plotly >= 1.30.0.

### 4. Rebuild JavaScript

```bash
cd src/js
npm install
npm run build

# Copy built file to vendor directory
cp build/kaleido_scopes.js ../py/kaleido/vendor/kaleido_scopes.js
```

### 5. Commit and Push

```bash
cd /Users/ryan/c/kaleido
git add src/js/src/plotly/render.js
git add src/py/kaleido/vendor/kaleido_scopes.js

git commit -m "Fix axref='x' annotations with plotly 6.x

The direct toImage() shortcut breaks with plotly 6.x when using
axref='x' or ayref='y' for data-coordinate annotation positioning.

This fix always uses newPlot() + toImage() approach for proper
axis initialization, which is needed for plotly 6.x's changed
figure serialization.

Fixes: Cannot read properties of undefined (reading 'val')
"

git push origin axref-fix
```

### 6. Test the Fork

```bash
# In a test environment
pip uninstall -y kaleido
pip install git+https://github.com/YOUR_USERNAME/kaleido.git@axref-fix#subdirectory=src/py

# Test it
cd /Users/ryan/c/hccs/path/kaleido-bug
python kaleido_axref_repro.py
```

Expected output:
```
✓ SUCCESS: Image saved to tmp/test_axref.png
```

## The Patch Details

### Before (Broken with plotly 6.x)

```javascript
if (semver.gte(Plotly.version, '1.30.0')) {
    promise = Plotly
      .toImage({ data: figure.data, layout: figure.layout, config: config }, imgOpts)
} else if (semver.gte(Plotly.version, '1.11.0')) {
    const gd = document.createElement('div')
    promise = Plotly
      .newPlot(gd, figure.data, figure.layout, config)
      .then(() => Plotly.toImage(gd, imgOpts))
      // ...
}
```

### After (Fixed)

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

        switch (format) {
          case 'png':
          case 'jpeg':
          case 'webp':
            if (encoded) {
              return imgData
            } else {
              return imgData.replace(cst.imgPrefix.base64, '')
            }
          case 'svg':
            if (encoded) {
              return imgData
            } else {
              return decodeSVG(imgData)
            }
          case 'pdf':
          case 'eps':
          case 'emf':
            return imgData
        }
      })
}
```

## Updating GitHub Actions

Once the fork is pushed, update `.github/workflows/test.yml`:

```yaml
- name: Install patched kaleido from fork
  run: |
    pip install git+https://github.com/YOUR_USERNAME/kaleido.git@axref-fix#subdirectory=src/py
```

And update `README.md` with the correct fork URL.

## Files Modified

- `src/js/src/plotly/render.js` - Core rendering logic
- `src/py/kaleido/vendor/kaleido_scopes.js` - Rebuilt JavaScript bundle

## Why This Fix Works

1. **Problem**: Plotly 6.x changed figure serialization, causing axis properties (specifically `.val` in autorange) to not be initialized when using the direct `toImage()` shortcut

2. **Solution**: The `newPlot()` approach:
   - Creates a graph div
   - Runs full plotly.js initialization
   - Sets up all axis properties including autorange
   - Enables proper coordinate transformations for `axref="x"` positioning

3. **Performance**: Minimal impact - this is what kaleido did for plotly < 1.30.0 anyway

## Testing Matrix

| Plotly | Kaleido | Result |
|--------|---------|--------|
| 5.24.1 | 0.2.1 (original) | ✅ Works |
| 6.3.1 | 0.2.1 (original) | ❌ Fails |
| 6.3.1 | 1.x (original) | ❌ Fails |
| 6.3.1 | 1.x (patched) | ✅ Works |
