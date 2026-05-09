import glob
import numpy as np

q_files = glob.glob('data/q_tables/*_qtable.npy')
coverage_stats = []

for f in q_files:
    qt = np.load(f)
    # A state is visited if any of its 3 actions have a non-zero Q-value
    visited_states = np.sum(np.any(qt != 0, axis=1))
    # Count total non-zero updates across the 243 (81x3) matrix
    nonzero_updates = np.count_nonzero(qt)
    coverage_stats.append((visited_states, nonzero_updates))

mean_visited = np.mean([x[0] for x in coverage_stats])
mean_updates = np.mean([x[1] for x in coverage_stats])

print("\n--- Q-Table Coverage Diagnostic (30 Seeds) ---")
print(f"Mean States Visited per Episode: {mean_visited:.1f} / 81 ({mean_visited/81*100:.1f}%)")
print(f"Mean Non-Zero (State, Action) Pairs: {mean_updates:.1f} / 243 ({mean_updates/243*100:.1f}%)")
print("----------------------------------------------")
print("Copy these exact numbers into the 'Limitations' and 'Learned Policy' sections.")