# Kaleido `axref="x"` Bug with Plotly 6.x

[![Test Status][badge]][gha-run]

**TL;DR:** Plotly 6.x breaks `axref="x"` annotations with all kaleido versions. [Patched kaleido fixes it][kaleido-fork].

## Minimal Reproduction

```python
import pandas as pd
import plotly.express as px

data = pd.DataFrame({'Value': [100, 200, 300]},
                   index=pd.date_range('2012-01', periods=3, freq='MS'))
fig = px.line(data)
idx = data.index.to_series()

fig.add_annotation(
    x=idx.iloc[-1], ax=idx.iloc[-2], axref="x",  # ← This breaks
    y=300, ay=350,
    text="Test"
)

fig.write_image('test.png')  # KaleidoError: Cannot read properties of undefined (reading 'val')
```

**Full script:** [`kaleido_axref_repro.py`](kaleido_axref_repro.py)

## Test Results

GitHub Actions [tests all combinations][gha-run]:

| Plotly | Kaleido | Result | Job |
|--------|---------|--------|-----|
| 5.24.1 | 0.2.1 | ✅ Pass | [Works with plotly 5.x][job-5.24] |
| 6.3.1 | 0.2.1 | ❌ Fail | [Plotly 6.x breaks][job-6.3-0.2] |
| 6.3.1 | 1.x | ❌ Fail | [Same error with 1.x][job-6.3-1.x] |
| 6.3.1 | patched | ✅ Pass | [**Fix works!**][job-patched] |

## The Fix

Install patched kaleido from [ryan-williams/Kaleido@axref-fix][kaleido-fork]:

```bash
pip install git+https://github.com/ryan-williams/Kaleido.git@axref-fix#subdirectory=src/py
```

**Root cause:** Plotly 6.x changed figure serialization. Kaleido's `toImage()` shortcut skips axis initialization needed for data-coordinate arrow positioning.

**Solution:** Always use `newPlot()` + `toImage()` approach for proper axis initialization. See [`render.js` changes][kaleido-diff].

## Files

- [`kaleido_axref_repro.py`](kaleido_axref_repro.py) - Minimal 20-line reproduction
- [`test_notebook_axref.py`](test_notebook_axref.py) - Real-world example from production notebook
- [`.github/workflows/test.yml`](.github/workflows/test.yml) - Automated test matrix

---

**Investigation:** [@runsascoded](https://github.com/runsascoded) with Claude Code

[badge]: https://github.com/ryan-williams/kaleido-bug/actions/workflows/test.yml/badge.svg
[gha-run]: https://github.com/ryan-williams/kaleido-bug/actions/runs/18825456806
[job-5.24]: https://github.com/ryan-williams/kaleido-bug/actions/runs/18825456806/job/50218095817
[job-6.3-0.2]: https://github.com/ryan-williams/kaleido-bug/actions/runs/18825456806/job/50218095907
[job-6.3-1.x]: https://github.com/ryan-williams/kaleido-bug/actions/runs/18825456806/job/50218095990
[job-patched]: https://github.com/ryan-williams/kaleido-bug/actions/runs/18825456806/job/50218096094
[kaleido-fork]: https://github.com/ryan-williams/Kaleido/tree/axref-fix
[kaleido-diff]: https://github.com/ryan-williams/Kaleido/commit/56961ab
