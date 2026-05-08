"""
Statistical analysis of BSE flash-crash experiment results.

Loads experiment results CSV and performs paired statistical tests
comparing baseline vs. treatment conditions across multiple seeds.
"""

import sys
import os
import argparse
from pathlib import Path
from typing import Dict, Tuple, Optional

import pandas as pd
import numpy as np
from scipy import stats

# Set up import paths
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


def load_and_pivot_results(csv_path: str) -> pd.DataFrame:
    """
    Load results CSV and pivot to seed-level analysis.

    Args:
        csv_path: Path to results_summary.csv

    Returns:
        DataFrame with seed as index and baseline/treatment columns
    """
    df = pd.read_csv(csv_path)

    # Verify required columns
    required_cols = {'seed', 'condition', 'mean_price', 'price_std', 'n_trades'}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"Missing required columns. Need: {required_cols}")

    # Verify conditions are baseline and treatment
    conditions = df['condition'].unique()
    if not {'baseline', 'treatment'}.issubset(conditions):
        raise ValueError(f"Expected conditions 'baseline' and 'treatment', got: {conditions}")

    # Pivot by seed
    pivoted = df.pivot_table(
        index='seed',
        columns='condition',
        values=['mean_price', 'price_std', 'n_trades'],
        aggfunc='first'
    )

    # Flatten column names
    pivoted.columns = [f"{col[1]}_{col[0]}" for col in pivoted.columns]

    # Reorder columns for clarity
    col_order = [
        'baseline_mean_price', 'treatment_mean_price',
        'baseline_price_std', 'treatment_price_std',
        'baseline_n_trades', 'treatment_n_trades'
    ]
    pivoted = pivoted[[col for col in col_order if col in pivoted.columns]]

    return pivoted


def compute_cohens_d(treatment: np.ndarray, baseline: np.ndarray) -> float:
    """
    Compute paired Cohen's d (d_z).

    Args:
        treatment: Treatment condition values
        baseline: Baseline condition values

    Returns:
        Cohen's d
    """
    diff = treatment - baseline
    return np.mean(diff) / np.std(diff, ddof=1)


def run_statistical_tests(
    treatment: np.ndarray,
    baseline: np.ndarray,
    metric_name: str
) -> Dict[str, float]:
    """
    Run three statistical tests comparing treatment vs baseline.

    Args:
        treatment: Treatment condition values
        baseline: Baseline condition values
        metric_name: Name of metric being tested (for logging)

    Returns:
        Dict with test results: paired_t_pval, welch_pval, cohens_d
    """
    # Paired t-test
    paired_t_stat, paired_t_pval = stats.ttest_rel(treatment, baseline)

    # Welch's t-test (doesn't assume equal variances)
    welch_t_stat, welch_pval = stats.ttest_ind(
        treatment, baseline, equal_var=False
    )

    # Cohen's d (paired)
    cohens_d = compute_cohens_d(treatment, baseline)

    return {
        'paired_t_pval': paired_t_pval,
        'welch_pval': welch_pval,
        'cohens_d': cohens_d
    }


def format_significance(pval: float) -> str:
    """
    Format p-value with significance markers.

    Args:
        pval: P-value

    Returns:
        Formatted p-value string with significance markers
    """
    if pval < 0.01:
        return f"{pval:.4f}**"
    elif pval < 0.05:
        return f"{pval:.4f}*"
    else:
        return f"{pval:.4f}"


def print_results_table(
    metric_name: str,
    baseline_vals: np.ndarray,
    treatment_vals: np.ndarray,
    test_results: Dict[str, float]
) -> None:
    """
    Print a formatted results table for one metric.

    Args:
        metric_name: Name of the metric
        baseline_vals: Baseline condition values
        treatment_vals: Treatment condition values
        test_results: Dict with test results
    """
    baseline_mean = np.mean(baseline_vals)
    treatment_mean = np.mean(treatment_vals)
    diff_mean = treatment_mean - baseline_mean

    print(f"\n{metric_name}")
    print("-" * 100)
    print(
        f"{'Metric':<20} | {'Mean Baseline':<15} | "
        f"{'Mean Treatment':<15} | {'Mean Diff':<12} | "
        f"{'Paired-t p':<12} | {'Welch p':<12} | {'Cohen d':<10}"
    )
    print("-" * 100)

    paired_p_str = format_significance(test_results['paired_t_pval'])
    welch_p_str = format_significance(test_results['welch_pval'])

    print(
        f"{metric_name:<20} | {baseline_mean:>14.4f} | "
        f"{treatment_mean:>14.4f} | {diff_mean:>11.4f} | "
        f"{paired_p_str:>12} | {welch_p_str:>12} | {test_results['cohens_d']:>9.4f}"
    )
    print("-" * 100)


def print_per_seed_table(
    pivoted_df: pd.DataFrame
) -> None:
    """
    Print per-seed breakdown table.

    Args:
        pivoted_df: Pivoted results DataFrame
    """
    print("\n\nPer-Seed Breakdown (Mean Price)")
    print("-" * 70)
    print(f"{'Seed':<10} | {'Baseline':<15} | {'Treatment':<15} | {'Difference':<15}")
    print("-" * 70)

    for seed, row in pivoted_df.iterrows():
        baseline = row['baseline_mean_price']
        treatment = row['treatment_mean_price']
        diff = treatment - baseline
        print(
            f"{seed:<10} | {baseline:>14.4f} | "
            f"{treatment:>14.4f} | {diff:>14.4f}"
        )

    print("-" * 70)


def save_summary_stats(
    pivoted_df: pd.DataFrame,
    treatment_means: np.ndarray,
    baseline_means: np.ndarray,
    treatment_stds: np.ndarray,
    baseline_stds: np.ndarray,
    mean_price_tests: Dict[str, float],
    volatility_tests: Dict[str, float],
    output_dir: str
) -> None:
    """
    Save summary statistics table to CSV.

    Args:
        pivoted_df: Pivoted results DataFrame
        treatment_means: Treatment mean prices
        baseline_means: Baseline mean prices
        treatment_stds: Treatment price stds
        baseline_stds: Baseline price stds
        mean_price_tests: Test results for mean price
        volatility_tests: Test results for volatility
        output_dir: Directory for output
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Create summary stats table
    summary_stats = {
        'Metric': ['Mean Price', 'Price Volatility (Std)'],
        'Baseline Mean': [
            np.mean(baseline_means),
            np.mean(baseline_stds)
        ],
        'Treatment Mean': [
            np.mean(treatment_means),
            np.mean(treatment_stds)
        ],
        'Mean Difference': [
            np.mean(treatment_means) - np.mean(baseline_means),
            np.mean(treatment_stds) - np.mean(baseline_stds)
        ],
        'Paired-t p-value': [
            mean_price_tests['paired_t_pval'],
            volatility_tests['paired_t_pval']
        ],
        'Welch p-value': [
            mean_price_tests['welch_pval'],
            volatility_tests['welch_pval']
        ],
        'Cohen d': [
            mean_price_tests['cohens_d'],
            volatility_tests['cohens_d']
        ]
    }

    summary_df = pd.DataFrame(summary_stats)
    output_path = os.path.join(output_dir, 'stats_output.csv')
    summary_df.to_csv(output_path, index=False)
    print(f"\n\nSummary stats saved to: {output_path}")


def main() -> None:
    """Main analysis orchestrator."""
    parser = argparse.ArgumentParser(
        description='Statistical analysis of BSE flash-crash experiment results'
    )
    parser.add_argument(
        '--input',
        type=str,
        default='data/mve/results_summary.csv',
        help='Path to results CSV (default: data/mve/results_summary.csv)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='results',
        help='Directory for output files (default: results)'
    )

    args = parser.parse_args()

    # Load and pivot data
    print(f"Loading results from: {args.input}")
    try:
        pivoted_df = load_and_pivot_results(args.input)
    except FileNotFoundError:
        print(f"Error: File not found: {args.input}")
        return
    except Exception as e:
        print(f"Error loading results: {e}")
        return

    print(f"Loaded {len(pivoted_df)} trials\n")

    # Extract arrays for testing
    baseline_means = pivoted_df['baseline_mean_price'].values
    treatment_means = pivoted_df['treatment_mean_price'].values
    baseline_stds = pivoted_df['baseline_price_std'].values
    treatment_stds = pivoted_df['treatment_price_std'].values

    # Run statistical tests
    mean_price_tests = run_statistical_tests(
        treatment_means, baseline_means, 'Mean Price'
    )
    volatility_tests = run_statistical_tests(
        treatment_stds, baseline_stds, 'Price Volatility'
    )

    # Print results tables
    print_results_table(
        'Mean Price',
        baseline_means,
        treatment_means,
        mean_price_tests
    )

    print_results_table(
        'Price Volatility (Std)',
        baseline_stds,
        treatment_stds,
        volatility_tests
    )

    print_per_seed_table(pivoted_df)

    # Save summary stats
    save_summary_stats(
        pivoted_df,
        treatment_means,
        baseline_means,
        treatment_stds,
        baseline_stds,
        mean_price_tests,
        volatility_tests,
        args.output_dir
    )

    print("\n✓ Analysis complete")


if __name__ == '__main__':
    main()
