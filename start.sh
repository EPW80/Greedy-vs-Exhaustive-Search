#!/usr/bin/env bash
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "=== Greedy vs Exhaustive Search ==="
echo ""

# --- Python virtual environment setup ---
if [ ! -d "venv" ]; then
  echo "[setup] Creating Python virtual environment..."
  python3 -m venv venv
fi

echo "[setup] Activating virtual environment..."
source venv/bin/activate

echo "[setup] Installing Python dependencies..."
pip install -q -r requirements.txt

# --- C++ build ---
echo ""
echo "[build] Compiling C++ sources..."
make maxweight_test maxweight_scatterplot

# --- Tests ---
echo ""
echo "[test] Running unit tests..."
make run_test

# --- Benchmark ---
echo ""
echo "[benchmark] Running benchmark (generates CSV data)..."
./maxweight_scatterplot

# --- Visualizations ---
echo ""
echo "[visualize] Generating plots..."
python3 visualize.py --all

echo ""
echo "=== Done ==="
echo "  Static plots:        plots/"
echo "  Interactive dashboard: plots/interactive_dashboard.html"
echo ""
echo "Open the dashboard with:"
echo "  xdg-open plots/interactive_dashboard.html   # Linux"
echo "  open plots/interactive_dashboard.html        # macOS"
