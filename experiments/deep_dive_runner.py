import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'src', 'bse'))
sys.path.insert(0, os.path.join(ROOT, 'src'))

from BSE import market_session
import BSE as _BSE
from agents.spoofer_v1 import SpooferV1
from agents.spoofer_q import SpooferQ
from experiment_runner import build_order_schedule  # Reuse your existing schedule

_BSE.trader_type_to_class['SPOOFER_V1'] = SpooferV1
_BSE.trader_type_to_class['SPOOFER_Q'] = SpooferQ


def run_deep_dive():
    anomaly_seeds = [49, 56, 64, 66, 71]
    conditions = ['baseline', 'treatment', 'treatment_v2']
    output_dir = 'data/deep_dive'
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # FULL MICROSCOPE ON
    dump_flags = {
        'dump_strats': True,  # Captures ZIP margin evolution
        'dump_lobs': True,  # Captures exact book state
        'dump_avgbals': True,
        'dump_tape': True,
        'dump_blotters': True  # Captures exact P/L for the Spoofer
    }

    order_sched = build_order_schedule(0.0, 600.0)

    for seed in anomaly_seeds:
        for cond in conditions:
            sess_id = os.path.join(output_dir, f"{cond}_seed{seed}")

            if cond == 'baseline':
                traders = {'sellers': [('ZIP', 25)], 'buyers': [('ZIP', 25)]}
            elif cond == 'treatment':
                traders = {'sellers': [('ZIP', 22), ('SPOOFER_V1', 3)], 'buyers': [('ZIP', 25)]}
            else:
                traders = {'sellers': [('ZIP', 22), ('SPOOFER_Q', 3)], 'buyers': [('ZIP', 25)]}

            print(f"Deep Dive: Running {cond} | Seed {seed}")
            market_session(sess_id, 0.0, 600.0, traders, order_sched, dump_flags, sess_vrbs=False)


if __name__ == '__main__':
    run_deep_dive()