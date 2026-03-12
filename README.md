# Greedy vs Exhaustive Search

**Author:** Erik Williams

## Overview

Implements and benchmarks two classic algorithm strategies for the knapsack problem using a real-world food database (8,063 items):

- **Greedy** — O(n²): sort by efficiency, pick greedily
- **Exhaustive** — O(2ⁿ): evaluate every possible combination for the optimal solution

The project compares runtime performance, solution quality, and approximation ratio between the two approaches, with full Python visualization tooling.

## Project Status

| Component | Status |
|-----------|--------|
| C++ algorithm implementations | Complete |
| Unit tests | Complete |
| Benchmark / scatter plot runner | Complete |
| Python visualization suite | Complete |
| Interactive HTML dashboard | Complete |

## Quick Start

```bash
# Full setup and run (recommended)
./start.sh
```

This script will:
1. Create and activate a Python virtual environment
2. Install Python dependencies
3. Compile C++ sources
4. Run unit tests
5. Run benchmarks (generates CSV data)
6. Generate all visualizations

## Manual Usage

```bash
# Install Python dependencies
pip install -r requirements.txt

# Build
make maxweight_test maxweight_scatterplot

# Run tests
make run_test

# Full workflow: test → benchmark → visualize
make all

# Generate static PNG plots only
make plots

# Generate interactive dashboard only
make interactive

# Clean build artifacts
make clean

# Clean everything including plots and CSVs
make clean_all
```

## Visualization

After running, outputs are saved to `plots/`:

| File | Description |
|------|-------------|
| `performance_comparison.png` | Execution time vs input size — exponential vs quadratic growth |
| `solution_quality.png` | Greedy approximation ratio vs optimal (exhaustive) |
| `theoretical_overlay.png` | Actual measurements fitted to O(n²) and O(2ⁿ) curves |
| `food_statistics.png` | Distribution of calories, weights, and efficiency across the food DB |
| `interactive_dashboard.html` | All plots in interactive format (zoom, pan, hover) |

Open the dashboard:
```bash
xdg-open plots/interactive_dashboard.html   # Linux
open plots/interactive_dashboard.html        # macOS
```

## Advanced Visualization Options

```bash
# Specific plots
python3 visualize.py --performance --quality

# Custom input files
python3 visualize.py --greedy my_greedy.csv --exhaustive my_exhaustive.csv

# Custom output directory
python3 visualize.py --output-dir my_plots/

python3 visualize.py --help
```

## Requirements

- **C++17** — g++ or g++-4.9
- **Python 3.7+** — matplotlib, pandas, seaborn, numpy, plotly, scipy

## Results

See [Greedy VS Exhaustive Search.pdf](./Greedy%20VS%20Exhaustive%20Search.pdf) for the full analysis report.
