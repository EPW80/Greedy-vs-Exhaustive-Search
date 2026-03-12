#!/usr/bin/env python3
"""
Visualization Suite for Greedy vs Exhaustive Search Analysis

Generates publication-quality static plots and interactive HTML dashboard
for algorithm performance comparison, solution quality analysis, and more.
"""

import argparse
import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
from scipy import stats
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class AlgorithmVisualizer:
    """Main visualization class for algorithm performance analysis."""

    def __init__(self, greedy_csv='greedy_detailed.csv',
                 exhaustive_csv='exhaustive_detailed.csv',
                 food_csv='food.csv',
                 output_dir='plots'):
        """
        Initialize the visualizer with data files.

        Args:
            greedy_csv: Path to greedy algorithm CSV file
            exhaustive_csv: Path to exhaustive search CSV file
            food_csv: Path to food database CSV file
            output_dir: Directory to save output plots
        """
        self.greedy_csv = greedy_csv
        self.exhaustive_csv = exhaustive_csv
        self.food_csv = food_csv
        self.output_dir = Path(output_dir)

        # Create output directory if it doesn't exist
        self.output_dir.mkdir(exist_ok=True)

        # Data containers
        self.greedy_data = None
        self.exhaustive_data = None
        self.food_data = None

        # Set style
        sns.set_style("whitegrid")
        sns.set_palette("husl")

    def load_data(self):
        """Load all CSV data files."""
        try:
            # Load algorithm performance data
            if os.path.exists(self.greedy_csv):
                self.greedy_data = pd.read_csv(self.greedy_csv)
                print(f"✓ Loaded {len(self.greedy_data)} greedy benchmarks")
            else:
                print(f"Warning: {self.greedy_csv} not found")

            if os.path.exists(self.exhaustive_csv):
                self.exhaustive_data = pd.read_csv(self.exhaustive_csv)
                print(f"✓ Loaded {len(self.exhaustive_data)} exhaustive benchmarks")
            else:
                print(f"Warning: {self.exhaustive_csv} not found")

            # Load food database
            if os.path.exists(self.food_csv):
                # Food CSV format: description^calories^weight
                self.food_data = pd.read_csv(
                    self.food_csv,
                    sep='^',
                    names=['description', 'calories', 'weight'],
                    encoding='utf-8'
                )
                # Convert numeric columns to proper types
                self.food_data['calories'] = pd.to_numeric(self.food_data['calories'], errors='coerce')
                self.food_data['weight'] = pd.to_numeric(self.food_data['weight'], errors='coerce')
                print(f"✓ Loaded {len(self.food_data)} food items")
            else:
                print(f"Warning: {self.food_csv} not found")

        except Exception as e:
            print(f"Error loading data: {e}")
            sys.exit(1)

    def plot_performance_comparison(self):
        """
        Create dual-axis performance comparison plot.
        Shows greedy O(n²) vs exhaustive O(2^n) growth.
        """
        if self.greedy_data is None or self.exhaustive_data is None:
            print("Skipping performance comparison - data not loaded")
            return

        fig, ax1 = plt.subplots(figsize=(12, 7))

        # Plot greedy on primary axis
        color1 = 'tab:blue'
        ax1.set_xlabel('Input Size (n)', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Greedy Time (seconds)', color=color1, fontsize=12, fontweight='bold')
        ax1.plot(self.greedy_data['n'], self.greedy_data['execution_time_sec'],
                color=color1, linewidth=2, label='Greedy O(n²)', alpha=0.8)
        ax1.tick_params(axis='y', labelcolor=color1)
        ax1.grid(True, alpha=0.3)

        # Plot exhaustive on secondary axis
        ax2 = ax1.twinx()
        color2 = 'tab:red'
        ax2.set_ylabel('Exhaustive Time (seconds)', color=color2, fontsize=12, fontweight='bold')
        ax2.plot(self.exhaustive_data['n'], self.exhaustive_data['execution_time_sec'],
                color=color2, linewidth=2, label='Exhaustive O(2^n)', alpha=0.8)
        ax2.tick_params(axis='y', labelcolor=color2)

        # Title and legend
        plt.title('Algorithm Performance Comparison: Greedy vs Exhaustive Search',
                 fontsize=14, fontweight='bold', pad=20)

        # Combined legend
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=11)

        plt.tight_layout()
        output_path = self.output_dir / 'performance_comparison.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_path}")
        plt.close()

    def plot_solution_quality(self):
        """
        Analyze solution quality: compare greedy approximation to optimal.
        Shows approximation ratio (greedy_weight / optimal_weight).
        """
        if self.greedy_data is None or self.exhaustive_data is None:
            print("Skipping solution quality - data not loaded")
            return

        # Merge data on 'n' for overlapping range (1-50)
        merged = pd.merge(
            self.greedy_data,
            self.exhaustive_data,
            on='n',
            suffixes=('_greedy', '_exhaustive')
        )

        # Calculate approximation ratio
        merged['approximation_ratio'] = (
            merged['weight_achieved_greedy'] / merged['weight_achieved_exhaustive']
        )

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

        # Plot 1: Weight comparison
        ax1.plot(merged['n'], merged['weight_achieved_greedy'],
                label='Greedy', linewidth=2, marker='o', markersize=3, alpha=0.7)
        ax1.plot(merged['n'], merged['weight_achieved_exhaustive'],
                label='Exhaustive (Optimal)', linewidth=2, marker='s', markersize=3, alpha=0.7)
        ax1.set_xlabel('Input Size (n)', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Total Weight Achieved (oz)', fontsize=12, fontweight='bold')
        ax1.set_title('Solution Weight: Greedy vs Optimal', fontsize=13, fontweight='bold')
        ax1.legend(fontsize=11)
        ax1.grid(True, alpha=0.3)

        # Plot 2: Approximation ratio
        ax2.plot(merged['n'], merged['approximation_ratio'] * 100,
                color='green', linewidth=2, marker='o', markersize=3)
        ax2.axhline(y=100, color='red', linestyle='--', alpha=0.5, label='100% (Optimal)')
        ax2.set_xlabel('Input Size (n)', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Approximation Quality (%)', fontsize=12, fontweight='bold')
        ax2.set_title('Greedy Approximation Quality', fontsize=13, fontweight='bold')
        ax2.legend(fontsize=11)
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim([85, 105])

        # Calculate statistics
        avg_ratio = merged['approximation_ratio'].mean()
        min_ratio = merged['approximation_ratio'].min()

        fig.text(0.5, 0.02,
                f'Average Approximation: {avg_ratio*100:.2f}% | '
                f'Worst Case: {min_ratio*100:.2f}%',
                ha='center', fontsize=11, style='italic')

        plt.tight_layout()
        output_path = self.output_dir / 'solution_quality.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_path}")
        plt.close()

    def plot_theoretical_overlay(self):
        """
        Overlay theoretical complexity curves on actual measurements.
        Fits O(n²) to greedy and O(2^n) to exhaustive data.
        """
        if self.greedy_data is None or self.exhaustive_data is None:
            print("Skipping theoretical overlay - data not loaded")
            return

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

        # === Greedy: Fit O(n²) ===
        n_greedy = self.greedy_data['n'].values
        t_greedy = self.greedy_data['execution_time_sec'].values

        # Polynomial fit (degree 2)
        coeffs = np.polyfit(n_greedy, t_greedy, 2)
        poly_fit = np.poly1d(coeffs)
        t_greedy_fit = poly_fit(n_greedy)

        ax1.scatter(n_greedy, t_greedy, alpha=0.5, s=20, label='Measured')
        ax1.plot(n_greedy, t_greedy_fit, 'r-', linewidth=2,
                label=f'Fit: {coeffs[0]:.2e}n² + {coeffs[1]:.2e}n + {coeffs[2]:.2e}')
        ax1.set_xlabel('Input Size (n)', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Execution Time (seconds)', fontsize=12, fontweight='bold')
        ax1.set_title('Greedy: Theoretical O(n²) Overlay', fontsize=13, fontweight='bold')
        ax1.legend(fontsize=10)
        ax1.grid(True, alpha=0.3)

        # R² calculation
        r2_greedy = 1 - (np.sum((t_greedy - t_greedy_fit)**2) /
                         np.sum((t_greedy - np.mean(t_greedy))**2))
        ax1.text(0.05, 0.95, f'R² = {r2_greedy:.6f}',
                transform=ax1.transAxes, fontsize=11,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        # === Exhaustive: Fit O(2^n) ===
        n_exhaustive = self.exhaustive_data['n'].values
        t_exhaustive = self.exhaustive_data['execution_time_sec'].values

        # Exponential fit
        def exponential_model(n, a, b):
            return a * (b ** n)

        try:
            # Use only points where time > 0 for fitting
            valid_idx = t_exhaustive > 0
            n_valid = n_exhaustive[valid_idx]
            t_valid = t_exhaustive[valid_idx]

            popt, _ = curve_fit(exponential_model, n_valid, t_valid,
                               p0=[1e-10, 2.0], maxfev=10000)
            t_exhaustive_fit = exponential_model(n_exhaustive, *popt)

            ax2.scatter(n_exhaustive, t_exhaustive, alpha=0.5, s=20, label='Measured')
            ax2.plot(n_exhaustive, t_exhaustive_fit, 'r-', linewidth=2,
                    label=f'Fit: {popt[0]:.2e} × {popt[1]:.4f}^n')

            # Calculate R²
            valid_fit = t_exhaustive_fit[valid_idx]
            r2_exhaustive = 1 - (np.sum((t_valid - valid_fit)**2) /
                                np.sum((t_valid - np.mean(t_valid))**2))
            ax2.text(0.05, 0.95, f'R² = {r2_exhaustive:.6f}',
                    transform=ax2.transAxes, fontsize=11,
                    verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        except Exception as e:
            print(f"Note: Could not fit exponential model: {e}")
            ax2.scatter(n_exhaustive, t_exhaustive, alpha=0.5, s=20, label='Measured')

        ax2.set_xlabel('Input Size (n)', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Execution Time (seconds)', fontsize=12, fontweight='bold')
        ax2.set_title('Exhaustive: Theoretical O(2^n) Overlay', fontsize=13, fontweight='bold')
        ax2.legend(fontsize=10)
        ax2.grid(True, alpha=0.3)
        ax2.set_yscale('log')

        plt.tight_layout()
        output_path = self.output_dir / 'theoretical_overlay.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_path}")
        plt.close()

    def plot_food_statistics(self):
        """
        Visualize food database statistics.
        Shows distribution of calories, weights, and efficiency ratios.
        """
        if self.food_data is None:
            print("Skipping food statistics - data not loaded")
            return

        # Calculate weight per calorie ratio
        self.food_data['weight_per_calorie'] = (
            self.food_data['weight'] / self.food_data['calories']
        )

        fig = plt.figure(figsize=(15, 10))
        gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)

        # Plot 1: Calorie distribution
        ax1 = fig.add_subplot(gs[0, 0])
        ax1.hist(self.food_data['calories'], bins=50, color='skyblue', edgecolor='black', alpha=0.7)
        ax1.set_xlabel('Calories', fontsize=11, fontweight='bold')
        ax1.set_ylabel('Frequency', fontsize=11, fontweight='bold')
        ax1.set_title('Distribution of Food Calories', fontsize=12, fontweight='bold')
        ax1.axvline(self.food_data['calories'].mean(), color='red',
                   linestyle='--', linewidth=2, label=f"Mean: {self.food_data['calories'].mean():.1f}")
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Plot 2: Weight distribution
        ax2 = fig.add_subplot(gs[0, 1])
        ax2.hist(self.food_data['weight'], bins=50, color='lightgreen', edgecolor='black', alpha=0.7)
        ax2.set_xlabel('Weight (oz)', fontsize=11, fontweight='bold')
        ax2.set_ylabel('Frequency', fontsize=11, fontweight='bold')
        ax2.set_title('Distribution of Food Weights', fontsize=12, fontweight='bold')
        ax2.axvline(self.food_data['weight'].mean(), color='red',
                   linestyle='--', linewidth=2, label=f"Mean: {self.food_data['weight'].mean():.1f}")
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        # Plot 3: Calories vs Weight scatter
        ax3 = fig.add_subplot(gs[1, 0])
        ax3.scatter(self.food_data['calories'], self.food_data['weight'],
                   alpha=0.3, s=10, c='purple')
        ax3.set_xlabel('Calories', fontsize=11, fontweight='bold')
        ax3.set_ylabel('Weight (oz)', fontsize=11, fontweight='bold')
        ax3.set_title('Calories vs Weight Relationship', fontsize=12, fontweight='bold')
        ax3.grid(True, alpha=0.3)

        # Add correlation
        corr = self.food_data['calories'].corr(self.food_data['weight'])
        ax3.text(0.05, 0.95, f'Correlation: {corr:.3f}',
                transform=ax3.transAxes, fontsize=10,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        # Plot 4: Weight per calorie ratio
        ax4 = fig.add_subplot(gs[1, 1])
        # Remove outliers for better visualization
        ratio_data = self.food_data['weight_per_calorie']
        ratio_clean = ratio_data[ratio_data < ratio_data.quantile(0.95)]
        ax4.hist(ratio_clean, bins=50, color='coral', edgecolor='black', alpha=0.7)
        ax4.set_xlabel('Weight per Calorie (oz/cal)', fontsize=11, fontweight='bold')
        ax4.set_ylabel('Frequency', fontsize=11, fontweight='bold')
        ax4.set_title('Food Efficiency: Weight per Calorie', fontsize=12, fontweight='bold')
        ax4.axvline(ratio_data.mean(), color='red',
                   linestyle='--', linewidth=2, label=f"Mean: {ratio_data.mean():.4f}")
        ax4.legend()
        ax4.grid(True, alpha=0.3)

        # Overall title
        fig.suptitle(f'Food Database Statistics (n={len(self.food_data)} items)',
                    fontsize=14, fontweight='bold', y=0.995)

        output_path = self.output_dir / 'food_statistics.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_path}")
        plt.close()

    def generate_interactive_dashboard(self):
        """
        Generate interactive HTML dashboard with all visualizations using Plotly.
        Creates a self-contained HTML file with zoom, pan, and hover capabilities.
        """
        if self.greedy_data is None or self.exhaustive_data is None:
            print("Skipping interactive dashboard - data not loaded")
            return

        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Performance Comparison', 'Solution Quality',
                          'Theoretical Overlay - Greedy', 'Food Statistics'),
            specs=[[{"secondary_y": True}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]],
            vertical_spacing=0.12,
            horizontal_spacing=0.1
        )

        # Plot 1: Performance Comparison (dual axis)
        fig.add_trace(
            go.Scatter(x=self.greedy_data['n'], y=self.greedy_data['execution_time_sec'],
                      name='Greedy O(n²)', mode='lines', line=dict(color='blue', width=2)),
            row=1, col=1, secondary_y=False
        )
        fig.add_trace(
            go.Scatter(x=self.exhaustive_data['n'], y=self.exhaustive_data['execution_time_sec'],
                      name='Exhaustive O(2^n)', mode='lines', line=dict(color='red', width=2)),
            row=1, col=1, secondary_y=True
        )

        # Plot 2: Solution Quality
        if len(self.exhaustive_data) > 0:
            merged = pd.merge(self.greedy_data, self.exhaustive_data, on='n', suffixes=('_greedy', '_exhaustive'))
            merged['approx_ratio'] = (merged['weight_achieved_greedy'] / merged['weight_achieved_exhaustive']) * 100

            fig.add_trace(
                go.Scatter(x=merged['n'], y=merged['approx_ratio'],
                          name='Approximation %', mode='lines+markers',
                          line=dict(color='green', width=2), marker=dict(size=4)),
                row=1, col=2
            )
            fig.add_hline(y=100, line_dash="dash", line_color="red",
                         annotation_text="100% Optimal", row=1, col=2)

        # Plot 3: Theoretical Overlay - Greedy
        n_greedy = self.greedy_data['n'].values
        t_greedy = self.greedy_data['execution_time_sec'].values
        coeffs = np.polyfit(n_greedy, t_greedy, 2)
        poly_fit = np.poly1d(coeffs)
        t_fit = poly_fit(n_greedy)

        fig.add_trace(
            go.Scatter(x=n_greedy, y=t_greedy, name='Measured',
                      mode='markers', marker=dict(size=4, color='blue', opacity=0.5)),
            row=2, col=1
        )
        fig.add_trace(
            go.Scatter(x=n_greedy, y=t_fit, name='O(n²) Fit',
                      mode='lines', line=dict(color='red', width=2)),
            row=2, col=1
        )

        # Plot 4: Food Calories Distribution
        if self.food_data is not None:
            fig.add_trace(
                go.Histogram(x=self.food_data['calories'], nbinsx=50,
                           name='Calorie Distribution', marker_color='skyblue'),
                row=2, col=2
            )

        # Update axes labels
        fig.update_xaxes(title_text="Input Size (n)", row=1, col=1)
        fig.update_yaxes(title_text="Greedy Time (s)", row=1, col=1, secondary_y=False)
        fig.update_yaxes(title_text="Exhaustive Time (s)", row=1, col=1, secondary_y=True)

        fig.update_xaxes(title_text="Input Size (n)", row=1, col=2)
        fig.update_yaxes(title_text="Approximation Quality (%)", row=1, col=2)

        fig.update_xaxes(title_text="Input Size (n)", row=2, col=1)
        fig.update_yaxes(title_text="Execution Time (s)", row=2, col=1)

        fig.update_xaxes(title_text="Calories", row=2, col=2)
        fig.update_yaxes(title_text="Frequency", row=2, col=2)

        # Update layout
        fig.update_layout(
            height=900,
            title_text="Greedy vs Exhaustive Search: Interactive Analysis Dashboard",
            title_font_size=20,
            showlegend=True,
            hovermode='x unified'
        )

        # Save interactive HTML (use CDN for Plotly.js to avoid inline script issues)
        output_path = self.output_dir / 'interactive_dashboard.html'
        fig.write_html(str(output_path), include_plotlyjs='cdn')
        print(f"✓ Saved: {output_path}")

    def generate_all_static(self):
        """Generate all static PNG visualizations."""
        print("\nGenerating static visualizations...")
        self.plot_performance_comparison()
        self.plot_solution_quality()
        self.plot_theoretical_overlay()
        self.plot_food_statistics()
        print("✓ All static plots generated successfully!")

    def generate_all(self):
        """Generate both static and interactive visualizations."""
        self.generate_all_static()
        print("\nGenerating interactive dashboard...")
        self.generate_interactive_dashboard()
        print("✓ All visualizations complete!")


def main():
    """Main entry point with CLI argument parsing."""
    parser = argparse.ArgumentParser(
        description='Visualize Greedy vs Exhaustive Search algorithm performance',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 visualize.py --all           # Generate all visualizations
  python3 visualize.py --static        # Static plots only
  python3 visualize.py --interactive   # Interactive dashboard only
  python3 visualize.py --performance --quality  # Specific plots
        """
    )

    parser.add_argument('--greedy', default='greedy_detailed.csv',
                       help='Path to greedy CSV file (default: greedy_detailed.csv)')
    parser.add_argument('--exhaustive', default='exhaustive_detailed.csv',
                       help='Path to exhaustive CSV file (default: exhaustive_detailed.csv)')
    parser.add_argument('--food', default='food.csv',
                       help='Path to food database CSV (default: food.csv)')
    parser.add_argument('--output-dir', default='plots',
                       help='Output directory for plots (default: plots)')

    # Visualization options
    parser.add_argument('--all', action='store_true',
                       help='Generate all visualizations (static + interactive)')
    parser.add_argument('--static', action='store_true',
                       help='Generate all static PNG plots')
    parser.add_argument('--interactive', action='store_true',
                       help='Generate interactive HTML dashboard')

    # Individual plots
    parser.add_argument('--performance', action='store_true',
                       help='Generate performance comparison plot')
    parser.add_argument('--quality', action='store_true',
                       help='Generate solution quality plot')
    parser.add_argument('--theoretical', action='store_true',
                       help='Generate theoretical overlay plot')
    parser.add_argument('--food-stats', action='store_true',
                       help='Generate food statistics plot')

    args = parser.parse_args()

    # Create visualizer
    viz = AlgorithmVisualizer(
        greedy_csv=args.greedy,
        exhaustive_csv=args.exhaustive,
        food_csv=args.food,
        output_dir=args.output_dir
    )

    # Load data
    print("Loading data...")
    viz.load_data()
    print()

    # Determine what to generate
    if args.all:
        viz.generate_all()
    elif args.static:
        viz.generate_all_static()
    elif args.interactive:
        viz.generate_interactive_dashboard()
    elif args.performance or args.quality or args.theoretical or args.food_stats:
        # Generate specific plots
        if args.performance:
            viz.plot_performance_comparison()
        if args.quality:
            viz.plot_solution_quality()
        if args.theoretical:
            viz.plot_theoretical_overlay()
        if args.food_stats:
            viz.plot_food_statistics()
    else:
        # Default: generate all static plots
        print("No visualization option specified, generating all static plots...")
        viz.generate_all_static()

    print(f"\n✓ Visualization complete! Outputs saved to '{args.output_dir}/' directory")
    print(f"  View plots: ls {args.output_dir}/")
    if os.path.exists(os.path.join(args.output_dir, 'interactive_dashboard.html')):
        print(f"  Open interactive dashboard: open {args.output_dir}/interactive_dashboard.html")


if __name__ == '__main__':
    main()
