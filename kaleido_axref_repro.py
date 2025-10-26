#!/usr/bin/env -S uv run --quiet --script
# /// script
# dependencies = [
#   "pandas",
#   "plotly",
#   "kaleido",
# ]
# ///
"""
Minimal reproduction of Kaleido 1.0.0+ regression with axref="x" annotations.

This script creates a simple line plot with annotations using axref="x" to
position arrows using data coordinates.

Works with: kaleido==0.2.1.post1
Breaks with: kaleido>=1.0.0 (Error: Cannot read properties of undefined (reading 'val'))

Usage:
    # Install kaleido 0.2.1 (works)
    pip install 'kaleido<1.0.0' 'plotly'
    python kaleido_axref_repro.py

    # Install kaleido 1.0.0+ (breaks)
    pip install 'kaleido>=1.0.0' 'plotly>=6.1.1'
    python kaleido_axref_repro.py
"""
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly

try:
    import kaleido
    kaleido_version = getattr(kaleido, '__version__', 'unknown')
except ImportError:
    kaleido_version = 'not installed'

print(f"Testing with kaleido=={kaleido_version}")
print(f"Testing with plotly=={plotly.__version__}")

# Create sample data
data = pd.DataFrame({
    'Avg Weekday': [252769, 261472, 269794, 260698, 261233],
    'Avg Weekend': [95527, 100742, 113074, 107867, 114421],
}, index=pd.date_range('2012-01', periods=5, freq='MS'))
data.index.name = 'month'

print("\nCreating figure with axref='x' annotation...")

# Create line plot
fig = px.line(data, labels={'value': 'Daily Rides', 'variable': ''})

# Add annotation using data coordinates for arrow positioning
# This is the pattern that breaks in kaleido 1.0.0+
idx = data.index.to_series()
x = idx.iloc[-1]  # Last data point
y = data['Avg Weekday'].iloc[-1]
x_str = x.strftime("%b '%y")
y_str = f"{y:,.0f}"

# The problematic annotation with axref="x"
fig.add_annotation(
    x=x,
    ax=idx.iloc[-3],  # Arrow tail at 3rd-from-last data point (data coordinates)
    axref="x",        # ← THIS BREAKS in kaleido 1.0.0+
    y=y,
    ayref="y",
    ay=y + 50000,     # Arrow tail 50k above the point (data coordinates)
    text=f'{x_str}: {y_str}',
)

print("Attempting to save as PNG...")

# Ensure output directory exists
output_path = Path(__file__).parent / 'test_axref.png'
output_path.parent.mkdir(exist_ok=True)

try:
    fig.write_image(str(output_path), width=700, height=500)
    print(f"✓ SUCCESS: Image saved to {output_path}")
    print("  This means axref='x' works with your kaleido version")
except Exception as e:
    print(f"✗ FAILED: {type(e).__name__}")
    print(f"  {e}")
    print("\n  This is the kaleido 1.0.0+ regression!")
    print("  The annotation with axref='x' causes kaleido to crash.")
    import sys
    sys.exit(1)
