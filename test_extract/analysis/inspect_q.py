import os
import glob
import numpy as np

# Point to the q_tables directory
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
q_dir = os.path.join(ROOT, 'data', 'q_tables')

# Find all saved Q-tables
q_files = glob.glob(os.path.join(q_dir, '*_qtable.npy'))

if not q_files:
    print(f"No Q-tables found in {q_dir}. Did the simulation run to completion?")
else:
    for q_file in q_files:
        qt = np.load(q_file)
        filename = os.path.basename(q_file)

        print(f"\n=== Inspection: {filename} ===")
        print(f"Non-zero cells: {np.count_nonzero(qt)} / 243")
        print(f"Max Q-value: {qt.max():.4f}")
        print(f"State visitation: {np.sum(qt != 0, axis=1).nonzero()[0].shape[0]} / 81 states visited")