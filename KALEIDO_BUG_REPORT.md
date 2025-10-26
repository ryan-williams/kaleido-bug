Annotations using `axref="x"` raise `KaleidoError` when exporting to PNG in Kaleido ≥1.0.0:

```
KaleidoError: Error 525: Cannot read properties of undefined (reading 'val')
```

## Reproduction

### Minimal Example

See `kaleido_axref_repro.py` - a standalone script that demonstrates the issue.

```python
import pandas as pd
import plotly.express as px

# Create sample data
data = pd.DataFrame({
    'Avg Weekday': [252769, 261472, 269794, 260698, 261233],
}, index=pd.date_range('2012-01', periods=5, freq='MS'))

fig = px.line(data)

# Add annotation with axref="x" (breaks in kaleido 1.0.0+)
idx = data.index.to_series()
fig.add_annotation(
    x=idx.iloc[-1],
    ax=idx.iloc[-3],  # Arrow tail using data coordinates
    axref="x",        # ← THIS BREAKS
    y=261233,
    ayref="y",
    ay=311233,
    text="May '12: 261,233",
)

# This line fails with kaleido 1.0.0+
fig.write_image('test.png')
```

### Test Both Versions

Run `./test_both_kaleido_versions.sh` to see:
1. ✓ Success with kaleido 0.2.1
2. ✗ Failure with kaleido 1.1.0

## Environment

```
kaleido==1.1.0      # BROKEN
plotly==6.3.1
Python 3.13.7
macOS 14.6 (arm64)
```

## Expected Behavior

The annotation should use data coordinates for the arrow tail position (`ax=idx.iloc[-3]`) just as it does for the arrow head (`x=idx.iloc[-1]`). This allows arrows to point from one data point to another.

## Actual Behavior

Kaleido crashes with `Cannot read properties of undefined (reading 'val')`.

## Workaround

1. **Pin to old kaleido** (temporary):
   ```toml
   kaleido<1.0.0
   ```

2. **Use pixel offsets** (loses data-aware positioning):
   ```python
   fig.add_annotation(
       x=x, y=y,
       text=text,
       ax=0, ay=-40,  # Fixed pixels instead of data coords
   )
   ```

3. **Remove axref** (but then ax is ignored):
   ```python
   fig.add_annotation(
       x=x, y=y,
       text=text,
       # No axref means ax/ay are in pixels
   )
   ```

## Impact

This breaks legitimate use cases where annotations need to point from one data point to another using data coordinates, which is particularly important for time series plots where pixel distances vary.

## Related Issues

- Kaleido v1.0.0 was a major rewrite (June 2024)
- Requires plotly>=6.1.1
- Removed bundled Chrome, changed API significantly

## Files

- `kaleido_axref_repro.py` - Minimal standalone reproduction
- `test_both_kaleido_versions.sh` - Test script for both versions
- `test_axref.png` - Output when it works (kaleido 0.2.1)
