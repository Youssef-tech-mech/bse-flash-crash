"""
Main experiment orchestrator for BSE flash-crash studies.

Runs controlled experiments comparing baseline (all ZIP) vs. treatment
(ZIP + spoofing agents) conditions across multiple random seeds.
Parses transaction data and computes summary statistics.
"""

import sys
import os
import argparse
import random
import csv
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, List, Any


# Set up import paths
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'src', 'bse'))
sys.path.insert(0, os.path.join(ROOT, 'src'))

from BSE import market_session
import BSE as _BSE
from agents.spoofer_v1 import SpooferV1
from agents.spoofer_q import SpooferQ
_BSE.trader_type_to_class['SPOOFER_V1'] = SpooferV1

# Register SpooferV1 with BSE's trader factory
_BSE.trader_type_to_class['SPOOFER_V1'] = SpooferV1
_BSE.trader_type_to_class['SPOOFER_Q'] = SpooferQ

def build_order_schedule(starttime: float, endtime: float) -> Dict[str, Any]:
    """
    Build a simple order schedule with fixed supply/demand ranges.

    Args:
        starttime: Session start time
        endtime: Session end time

    Returns:
        Order schedule dict for BSE market_session
    """
    # Price ranges: supply 80-120, demand 80-120
    range_supply = (80, 100)
    range_demand = (80, 120)

    supply_schedule = [
        {
            'from': starttime,
            'to': endtime,
            'ranges': [range_supply],
            'stepmode': 'fixed'
        }
    ]

    demand_schedule = [
        {
            'from': starttime,
            'to': endtime,
            'ranges': [range_demand],
            'stepmode': 'fixed'
        }
    ]

    order_sched = {
        'sup': supply_schedule,
        'dem': demand_schedule,
        'interval': 1,
        'timemode': 'drip-poisson'
    }

    return order_sched


def parse_tape_csv(tape_path: str) -> Optional[Dict[str, float]]:
    """
    Parse transaction tape CSV and compute statistics.
    """
    if not os.path.exists(tape_path):
        return None

    try:
        prices = []
        with open(tape_path, 'r') as f:
            reader = csv.reader(f)
            # No next(reader) here, start reading immediately!
            for row in reader:
                # Defensively skip empty rows or non-TRD events
                if len(row) < 3 or row[0].strip() != 'TRD':
                    continue
                try:
                    # Index 2 is the price! (e.g., TRD, 7.600000, 93)
                    price = float(row[2])
                    prices.append(price)
                except ValueError:
                    continue

        if not prices:
            return None

        mean_price = sum(prices) / len(prices)
        variance = sum((p - mean_price) ** 2 for p in prices) / len(prices)
        price_std = variance ** 0.5

        return {
            'mean_price': mean_price,
            'price_std': price_std,
            'n_trades': len(prices)
        }
    except Exception as e:
        print(f"  Warning: Failed to parse {tape_path}: {e}")
        return None

def run_trial(
    seed: int,
    condition: str,
    starttime: float,
    endtime: float,
    output_dir: str
) -> Optional[Dict[str, Any]]:
    """
    Run a single market session trial.

    Args:
        seed: Random seed
        condition: 'baseline' or 'treatment'
        starttime: Session start time
        endtime: Session end time
        output_dir: Directory for output files

    Returns:
        Dict with trial results or None on failure
    """
    # Set random seed
    random.seed(seed)

    # Create session ID
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    sess_name = f"{condition}_seed{seed}"
    sess_id = os.path.join(output_dir, sess_name)
    # Build trader specs
    if condition == 'baseline':
        traders_spec = {
            'sellers': [('ZIP', 25)],
            'buyers': [('ZIP', 25)]
        }
    elif condition == 'treatment':
        traders_spec = {
            'sellers': [('ZIP', 22), ('SPOOFER_V1', 3)],
            'buyers': [('ZIP', 25)]
        }
    elif condition == 'treatment_v2':
        traders_spec = {
            'sellers': [('ZIP', 22), ('SPOOFER_Q', 3)],
            'buyers': [('ZIP', 25)]
        }
    else:
        raise ValueError(f"Unknown condition: {condition}")

    # Build order schedule
    order_sched = build_order_schedule(starttime, endtime)

    # Dump flags
    dump_flags = {
        'dump_strats': False,
        'dump_lobs': False,
        'dump_avgbals': True,
        'dump_tape': True,
        'dump_blotters': False
    }

    # Ensure output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Run market session
    try:
        print(f"  Running {condition} with seed {seed}...")
        market_session(
            sess_id,
            starttime,
            endtime,
            traders_spec,
            order_sched,
            dump_flags,
            sess_vrbs=False
        )

        # Parse results - sess_id already contains the output_dir!
        tape_path = f"{sess_id}_tape.csv"

        stats = parse_tape_csv(tape_path)
        if stats is None:
            print(f"  Warning: Could not parse tape for {sess_id}")
            return None

        result = {
            'seed': seed,
            'condition': condition,
            'mean_price': stats['mean_price'],
            'price_std': stats['price_std'],
            'n_trades': stats['n_trades']
        }

        return result

    except Exception as e:
        print(f"  Error running trial {sess_id}: {e}")
        return None




def main() -> None:
    """Main experiment orchestrator."""
    parser = argparse.ArgumentParser(
        description='Run BSE flash-crash experiments with spoofing agents'
    )
    parser.add_argument(
        '--seeds',
        type=int,
        nargs='+',
        default=[42, 43, 44, 45, 46],
        help='Random seeds for trials (default: 42 43 44 45 46)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='data/mve',
        help='Directory for output files (default: data/mve)'
    )

    parser.add_argument(
        '--conditions', type=str, nargs='+', default=['baseline', 'treatment'],
        help='Conditions to run (e.g. baseline treatment treatment_v2)'
    )

    args = parser.parse_args()
    conditions = args.conditions

    # Experiment parameters
    starttime = 0.0
    endtime = 600.0

    # Collect results
    all_results = []

    print(f"\nStarting experiments with seeds: {args.seeds}")
    print(f"Output directory: {args.output_dir}\n")

    for seed in args.seeds:
        for condition in conditions:
            result = run_trial(seed, condition, starttime, endtime, args.output_dir)
            if result is not None:
                all_results.append(result)

    # Save results to CSV
    if all_results:
        df = pd.DataFrame(all_results)
        results_path = os.path.join(args.output_dir, 'results_summary.csv')
        df.to_csv(results_path, index=False)
        print(f"\nResults saved to {results_path}")
        print(f"Total trials: {len(all_results)}")
    else:
        print("\nNo trials completed successfully.")


if __name__ == '__main__':
    main()
