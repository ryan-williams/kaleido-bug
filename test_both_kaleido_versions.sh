#!/bin/bash
# Test script to demonstrate kaleido axref regression
# Runs the repro script with both kaleido 0.2.1 (works) and 1.1.0 (breaks)

set -e

cd "$(dirname "$0")"

echo "=============================================="
echo "Testing with Kaleido 0.2.1 (SHOULD WORK)"
echo "=============================================="
pip install -q 'kaleido<1.0.0' 'plotly>=6.1.1'
python3 kaleido_axref_repro.py
echo ""

echo "=============================================="
echo "Testing with Kaleido 1.1.0 (SHOULD FAIL)"
echo "=============================================="
pip install -q 'kaleido>=1.1.0' 'plotly>=6.1.1'
python3 kaleido_axref_repro.py || echo "^ Expected failure with kaleido 1.1.0"
echo ""

echo "=============================================="
echo "Restoring Kaleido 0.2.1"
echo "=============================================="
pip install -q 'kaleido<1.0.0'
echo "Done"
