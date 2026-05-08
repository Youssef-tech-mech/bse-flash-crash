"""
Generate paper-ready figures for BSE flash-crash study.

Creates grouped bar charts and difference plots comparing baseline vs.
treatment (spoofing) conditions across multiple random seeds.
"""

import sys
import os
import argparse
from pathlib import Path
from typing import Tuple

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

# Set up import paths
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


def load_and_organize_data(csv_path: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load results CSV and organize by condition.

    Args:
        csv_path: Path to results_summary.csv

    Returns:
        Tuple of (baseline_df, treatment_df) sorted by seed
    """
    df = pd.read_csv(csv_path)

    baseline_df = df[df['condition'] == 'baseline'].sort_values('seed')
    treatment_df = df[df['condition'] == 'treatment'].sort_values('seed')

    return baseline_df, treatment_df


def create_figure1_mean_price_comparison(
    baseline_df: pd.DataFrame,
    treatment_df: pd.DataFrame,
    figures_dir: str
) -> None:
    """
    Create grouped bar chart comparing mean prices by seed.

    Args:
        baseline_df: Baseline condition results
        treatment_df: Treatment condition results
        figures_dir: Directory to save figures
    """
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(10, 6))

    seeds = baseline_df['seed'].values
    baseline_means = baseline_df['mean_price'].values
    treatment_means = treatment_df['mean_price'].values

    # Bar positions
    x = np.arange(len(seeds))
    width = 0.35

    # Create bars
    bars1 = ax.bar(x - width/2, baseline_means, width, label='Baseline (ZIP only)',
                   color='steelblue', edgecolor='black', linewidth=0.5)
    bars2 = ax.bar(x + width/2, treatment_means, width, label='Treatment (ZIP + SpooferV1)',
                   color='crimson', edgecolor='black', linewidth=0.5)

    # Grand mean of baseline (horizontal dashed line)
    baseline_grand_mean = np.mean(baseline_means)
    ax.axhline(y=baseline_grand_mean, color='grey', linestyle='--', linewidth=1.5,
               alpha=0.7, label=f'Baseline Mean: {baseline_grand_mean:.2f}')

    # Add value labels on bars
    def add_labels(bars):
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}',
                   ha='center', va='bottom', fontsize=10)

    add_labels(bars1)
    add_labels(bars2)

    # Labels and title
    ax.set_xlabel('Random Seed', fontsize=12)
    ax.set_ylabel('Mean Transaction Price (£)', fontsize=12)
    ax.set_title('Mean Transaction Price: Baseline vs. V1 Spoofer (5-Seed MVE)',
                fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(seeds, fontsize=10)
    ax.tick_params(axis='y', labelsize=10)
    ax.legend(fontsize=11, loc='upper left', bbox_to_anchor=(1.02, 1))
    ax.grid(True, alpha=0.3, axis='y')

    # Save figure
    Path(figures_dir).mkdir(parents=True, exist_ok=True)
    save_path = os.path.join(figures_dir, 'fig1_mean_price_comparison.pdf')
    plt.savefig(save_path, bbox_inches='tight', dpi=150)
    print(f"Saved: {save_path}")
    plt.close()


def create_figure2_price_impact_per_seed(
    baseline_df: pd.DataFrame,
    treatment_df: pd.DataFrame,
    figures_dir: str
) -> None:
    """
    Create horizontal bar chart showing price difference per seed.

    Args:
        baseline_df: Baseline condition results
        treatment_df: Treatment condition results
        figures_dir: Directory to save figures
    """
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(10, 6))

    seeds = baseline_df['seed'].values
    baseline_means = baseline_df['mean_price'].values
    treatment_means = treatment_df['mean_price'].values

    # Compute differences
    diffs = treatment_means - baseline_means
    mean_diff = np.mean(diffs)

    # Colors based on direction
    colors = ['crimson' if d < 0 else 'steelblue' for d in diffs]

    # Create horizontal bars
    y_pos = np.arange(len(seeds))
    ax.barh(y_pos, diffs, color=colors, edgecolor='black', linewidth=0.5)

    # Vertical line at x=0
    ax.axvline(x=0, color='black', linestyle='-', linewidth=1)

    # Vertical line at mean difference with annotation
    ax.axvline(x=mean_diff, color='navy', linestyle='--', linewidth=2,
               label=f'Mean Effect: {mean_diff:.2f}')
    ax.text(mean_diff, len(seeds) - 0.5, f'{mean_diff:.2f}',
           fontsize=10, ha='left', va='top', color='navy', fontweight='bold')

    # Labels and title
    ax.set_xlabel('Price Difference: Treatment − Baseline (£)', fontsize=12)
    ax.set_ylabel('Random Seed', fontsize=12)
    ax.set_title('Per-Seed Price Impact of SpooferV1', fontsize=14, fontweight='bold')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(seeds, fontsize=10)
    ax.tick_params(axis='x', labelsize=10)
    ax.legend(fontsize=11, loc='upper right')
    ax.grid(True, alpha=0.3, axis='x')

    # Save figure
    Path(figures_dir).mkdir(parents=True, exist_ok=True)
    save_path = os.path.join(figures_dir, 'fig2_price_impact_per_seed.pdf')
    plt.savefig(save_path, bbox_inches='tight', dpi=150)
    print(f"Saved: {save_path}")
    plt.close()


def main() -> None:
    """Main figure generation orchestrator."""
    parser = argparse.ArgumentParser(
        description='Generate paper-ready figures for BSE flash-crash study'
    )
    parser.add_argument(
        '--input',
        type=str,
        default='data/mve/results_summary.csv',
        help='Path to results CSV (default: data/mve/results_summary.csv)'
    )
    parser.add_argument(
        '--figures-dir',
        type=str,
        default='figures',
        help='Directory for output figures (default: figures)'
    )

    args = parser.parse_args()

    # Load data
    print(f"Loading results from: {args.input}")
    try:
        baseline_df, treatment_df = load_and_organize_data(args.input)
    except FileNotFoundError:
        print(f"Error: File not found: {args.input}")
        return
    except Exception as e:
        print(f"Error loading results: {e}")
        return

    print(f"Loaded {len(baseline_df)} baseline trials, {len(treatment_df)} treatment trials\n")

    # Generate figures
    print("Generating figures...")
    create_figure1_mean_price_comparison(baseline_df, treatment_df, args.figures_dir)
    create_figure2_price_impact_per_seed(baseline_df, treatment_df, args.figures_dir)

    print("\n✓ All figures generated successfully")


if __name__ == '__main__':
    main()
