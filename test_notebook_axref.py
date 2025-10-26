#!/usr/bin/env -S uv run --quiet --script
# /// script
# dependencies = [
#   "pandas",
#   "plotly>=6.0.0",
#   "kaleido",
#   "fastparquet",
# ]
# ///
"""
Minimal script extracted from months.ipynb that uses axref="x" annotations.
This tests whether kaleido can handle the actual notebook's annotation pattern.
"""
import pandas as pd
import plotly.express as px
import sys
from os.path import dirname, join

# Load aggregated data from parent directory
data_dir = join(dirname(__file__), '..', 'data')
m = pd.read_parquet(join(data_dir, 'all.pqt'))

try:
    import kaleido
    kaleido_version = kaleido.__version__
except AttributeError:
    kaleido_version = "unknown"

import plotly
print(f"Testing with kaleido=={kaleido_version}")
print(f"Testing with plotly=={plotly.__version__}")
print()

# Convert month string back to datetime
m['month'] = pd.to_datetime(m['month'])

# Aggregate by month (same as notebook cell 13)
mt = m.drop(columns='station').groupby('month').sum()

# Create the exact plot from notebook cell 29 (avg_day_types)
df = mt[['avg weekday', 'avg weekend']].rename(columns={
    'avg weekday': 'Avg Weekday',
    'avg weekend': 'Avg Weekend',
})

print("Creating line plot with axref='x' annotations...")
fig = px.line(
    df,
    labels={
        'variable': '',
        'value': 'Daily Rides',
        'month': '',
    }
)

# Add annotations with axref="x" and ayref="y" (same as notebook)
idx = df.index.to_series()
ax_offset = 13
ay_offsets = [50_000, -50_000]

for k, ay_offset in zip(df, ay_offsets):
    x = idx.iloc[-1]
    y = df[k].iloc[-1]
    x_str = x.strftime("%b '%y")
    y_str = format(y, ',.0f')
    fig.add_annotation(
        x=x, axref="x",
        y=y, ayref="y",
        ax=idx.iloc[-ax_offset],
        ay=y + ay_offset,
        text=f'{x_str}: {y_str}',
    )

print("Attempting to save as PNG...")
output = join(dirname(__file__), 'tmp', 'test_notebook_axref.png')
try:
    fig.write_image(output)
    print(f"✓ SUCCESS: PNG saved to {output}")
    sys.exit(0)
except Exception as e:
    print(f"✗ FAILED: {e.__class__.__name__}")
    print(f"  {e}")
    sys.exit(1)
