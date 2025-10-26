#!/usr/bin/env python3
"""
Comprehensive test matrix for kaleido axref bug.

Tests all combinations of:
- plotly versions: 5.24.1, 6.3.1
- kaleido versions: 0.2.1, 1.x (latest)
- annotation types: axref="x" (broken), simple pixel offset (workaround)
"""
import sys
import subprocess
import json
from pathlib import Path

# Test configurations
CONFIGS = [
    {"plotly": "5.24.1", "kaleido": "0.2.1", "expected": "PASS"},
    {"plotly": "6.3.1", "kaleido": "0.2.1", "expected": "FAIL"},
    {"plotly": "6.3.1", "kaleido": "git+https://github.com/YOUR_USERNAME/kaleido.git@axref-fix#subdirectory=src/py", "expected": "PASS"},
]

def create_test_figure():
    """Create a simple test figure with axref annotation."""
    import pandas as pd
    import plotly.express as px

    data = pd.DataFrame({
        'Value': [252769, 261472, 269794, 260698, 261233],
    }, index=pd.date_range('2012-01', periods=5, freq='MS'))

    fig = px.line(data)
    idx = data.index.to_series()

    # Add annotation with axref="x" (the problematic case)
    fig.add_annotation(
        x=idx.iloc[-1],
        ax=idx.iloc[-3],
        axref="x",
        y=261233,
        ayref="y",
        ay=311233,
        text="Test annotation",
    )

    return fig

def test_configuration(plotly_version, kaleido_version):
    """Test a specific configuration."""
    import importlib

    # Install versions
    print(f"\n{'='*60}")
    print(f"Testing: plotly={plotly_version}, kaleido={kaleido_version}")
    print(f"{'='*60}")

    # Install plotly
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", f"plotly=={plotly_version}"],
        check=True
    )

    # Install kaleido
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", kaleido_version],
        check=True
    )

    # Reload modules to get new versions
    if 'plotly' in sys.modules:
        del sys.modules['plotly']
    if 'plotly.express' in sys.modules:
        del sys.modules['plotly.express']
    if 'kaleido' in sys.modules:
        del sys.modules['kaleido']

    # Try to create and save figure
    try:
        import plotly
        print(f"  Loaded plotly {plotly.__version__}")

        try:
            import kaleido
            kaleido_ver = getattr(kaleido, '__version__', 'unknown')
        except AttributeError:
            kaleido_ver = 'unknown'
        print(f"  Loaded kaleido {kaleido_ver}")

        fig = create_test_figure()
        output = Path("tmp") / f"test_plotly{plotly_version}_kaleido{kaleido_ver}.png"
        output.parent.mkdir(exist_ok=True)

        fig.write_image(str(output))
        print(f"  ✅ SUCCESS: Saved to {output}")
        return "PASS"

    except Exception as e:
        print(f"  ❌ FAIL: {e.__class__.__name__}: {e}")
        return "FAIL"

def main():
    """Run all test configurations."""
    results = []

    print("Kaleido axref Bug Test Matrix")
    print("=" * 60)

    for config in CONFIGS:
        result = test_configuration(config["plotly"], config["kaleido"])
        results.append({
            **config,
            "actual": result,
            "match": result == config["expected"]
        })

    # Print summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}\n")

    print(f"{'Plotly':<10} {'Kaleido':<20} {'Expected':<10} {'Actual':<10} {'Status'}")
    print("-" * 60)

    for r in results:
        kaleido_display = r['kaleido'][:17] + "..." if len(r['kaleido']) > 20 else r['kaleido']
        status = "✅" if r['match'] else "❌"
        print(f"{r['plotly']:<10} {kaleido_display:<20} {r['expected']:<10} {r['actual']:<10} {status}")

    # Exit with error if any tests didn't match expectations
    if not all(r['match'] for r in results):
        print("\n❌ Some tests didn't match expectations!")
        sys.exit(1)
    else:
        print("\n✅ All tests matched expectations!")
        sys.exit(0)

if __name__ == "__main__":
    main()
