import os
import glob
import numpy as np
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
q_dir = os.path.join(ROOT, 'data', 'q_tables')
q_files = glob.glob(os.path.join(q_dir, '*_qtable.npy'))

if not q_files:
    print("No Q-tables found!")
    exit()

# Aggregate all Q-tables
master_q = np.zeros((81, 3))
for f in q_files:
    master_q += np.load(f)

# Average them to find the true learned policy
master_q /= len(q_files)

# Extract the value of the AGGRESS action (Column 1)
aggress_values = master_q[:, 1]
# Reshape the 81 states into a 9x9 grid for visualization
# We will use Time Remaining (tr) and Price Direction (pd) as one axis,
# and Order Book Imbalance (obi) and Price to Limit (pt) as the other.
heatmap_data = aggress_values.reshape((9, 9))

plt.figure(figsize=(10, 8))
plt.imshow(heatmap_data, cmap='inferno', aspect='auto')
plt.colorbar(label='Average Q-Value (Reward for crashing price)')
plt.title('V2 Spoofer Learned Policy: Aggressiveness Heatmap\n(Aggregated over 30 Seeds)')
plt.xlabel('Market State (OBI & PT)')
plt.ylabel('Market State (Time & PD)')

# Add grid lines
plt.grid(False)

# Save the figure
out_path = os.path.join(ROOT, 'figures', 'q_table_heatmap.pdf')
os.makedirs(os.path.dirname(out_path), exist_ok=True)
plt.savefig(out_path, bbox_inches='tight', dpi=150)
print(f"Heatmap saved to {out_path}")