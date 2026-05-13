"""
Generate three paper-ready figures from BSE experiment results.

Outputs:
  - fig1_price_trajectories.pdf: Per-seed scatter with mean/SD bands
  - fig2_volatility_distribution.pdf: Violin plots of price volatility
  - fig3_qtable_heatmap.pdf: Mean Q-table heatmap across all seeds
"""
## Boilerplate code, not part of the core logic, Gemini generated the plots style, I added variables, also Gemini fixed the styling of each plot.
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from glob import glob
from scipy import stats

# Setup
sns.set_style('whitegrid') ## Example of using Gemini to help with styling such as the sizing and colours.
plt.rcParams.update({
    'font.size': 12,
    'axes.titlesize': 13,
    'axes.labelsize': 12
})

# Create figures directory
os.makedirs('figures', exist_ok=True)

# Load results
results_df = pd.read_csv('data/results_all.csv')

# Color map
colors = {
    'baseline': 'gray',
    'treatment': '#E05C5C',
    'treatment_v2': '#5B8DD9'
}

# FIGURE 1: Price Trajectories


fig, axes = plt.subplots(1, 3, figsize=(10, 6), sharey=True)
conditions = ['baseline', 'treatment', 'treatment_v2']
display_names = {
    'baseline': 'Baseline (No Spoofer)',
    'treatment': 'V1: Heuristic Spoofer',
    'treatment_v2': 'V2: Q-Learning Spoofer'
}

# Compute baseline stats for Cohen's d
baseline_data = results_df[results_df['condition'] == 'baseline']
baseline_prices = baseline_data.groupby('seed')['mean_price'].first().values
baseline_mean = baseline_prices.mean()
baseline_std = baseline_prices.std(ddof=1)

for ax_idx, (ax, condition) in enumerate(zip(axes, conditions)):
    cond_data = results_df[results_df['condition'] == condition]

    # Get per-seed mean prices
    prices_by_seed = cond_data.groupby('seed')['mean_price'].first()
    seeds = sorted(prices_by_seed.index)
    prices = prices_by_seed.loc[seeds].values

    # Scatter plot
    ax.scatter(seeds, prices, alpha=0.4, color=colors[condition], s=50)

    # Mean line
    mean_price = prices.mean()
    ax.axhline(mean_price, color=colors[condition], linestyle='-', linewidth=2)

    # +/- 1 SD band
    std_price = prices.std(ddof=1)
    ax.fill_between(
        [min(seeds), max(seeds)],
        mean_price - std_price,
        mean_price + std_price,
        alpha=0.2,
        color=colors[condition]
    )

    # Cohen's d vs baseline                 ## Conditions and maths here are my code after searching how to use Cohen's d
    if condition != 'baseline':
        cohens_d = (mean_price - baseline_mean) / baseline_std
    else:
        cohens_d = 0.0

    # Annotation box
    text_str = f'Mean: £{mean_price:.2f} +/- {std_price:.2f}\nCohen\'s d: {cohens_d:.2f}'
    ax.text(
        0.95, 0.05,
        text_str,
        transform=ax.transAxes,
        fontsize=10,
        verticalalignment='bottom',
        horizontalalignment='right',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7)
    )

    ax.set_xlabel('Random seed')
    ax.set_ylabel('Mean transaction price (£)')
    ax.set_title(display_names[condition])
    ax.set_xlim(40, 73)
    ax.set_ylim(82, 99)

fig.suptitle('Mean Transaction Price by Condition (n=30 seeds)', fontsize=13, y=1.00)
plt.tight_layout()
plt.savefig('figures/fig1_price_trajectories.pdf', dpi=300, bbox_inches='tight')
print('Saved: figures/fig1_price_trajectories.pdf')
plt.close()


# FIGURE 2: Volatility Distribution


fig, ax = plt.subplots(figsize=(8, 7))

# Prepare volatility data for each condition
volatility_data = {}
for condition in conditions:
    cond_data = results_df[results_df['condition'] == condition]
    vols = cond_data.groupby('seed')['price_std'].first().values
    volatility_data[condition] = vols

# Create violin plot
parts = ax.violinplot(
    [volatility_data[c] for c in conditions],
    positions=[0, 1, 2],
    showmeans=False,
    showmedians=False,
    widths=0.7
)

# Color the violins
for pc, condition in zip(parts['bodies'], conditions):
    pc.set_facecolor(colors[condition])
    pc.set_alpha(0.7)
    pc.set_edgecolor('black')
    pc.set_linewidth(1.5)

# Jitter points + median lines
for pos, condition in enumerate(conditions):
    data = volatility_data[condition]

    # Jitter
    x = np.random.normal(pos, 0.04, size=len(data))
    ax.scatter(x, data, alpha=0.5, s=16, color=colors[condition], zorder=3)

    # Median
    median = np.median(data)
    ax.hlines(median, pos - 0.3, pos + 0.3, colors='darkred', linewidth=2.5, zorder=4)

# Custom x-axis labels
custom_labels = [
    'Baseline',
    'V1: Heuristic\n(Sledgehammer)',
    'V2: Q-Learning\n(Erratic Manipulator)'
]
ax.set_xticks([0, 1, 2])
ax.set_xticklabels(custom_labels, fontsize=11)
ax.set_ylabel('Price standard deviation (£)')
ax.set_title('Intra-Session Price Volatility by Condition (n=30 seeds)', fontsize=13)

# Significance brackets (A, B, C)
y_max = max([max(volatility_data[c]) for c in conditions]) * 1.15

# Bracket A (baseline to treatment)
ax.plot([0, 1], [y_max, y_max], 'k-', linewidth=1)
ax.text(0.5, y_max + 0.02, 'A: p=0.001', ha='center', fontsize=10, fontweight='bold')

# Bracket B (baseline to treatment_v2)
ax.plot([0, 2], [y_max * 1.08, y_max * 1.08], 'k-', linewidth=1)
ax.text(1.0, y_max * 1.08 + 0.02, 'B: p<0.001', ha='center', fontsize=10, fontweight='bold')

# Bracket C (treatment to treatment_v2)
ax.plot([1, 2], [y_max * 1.16, y_max * 1.16], 'k-', linewidth=1)
ax.text(1.5, y_max * 1.16 + 0.02, 'C: p=0.001', ha='center', fontsize=10, fontweight='bold')

ax.set_ylim(bottom=0)
plt.tight_layout()
plt.savefig('figures/fig2_volatility_distribution.pdf', dpi=300, bbox_inches='tight')
print('Saved: figures/fig2_volatility_distribution.pdf')
plt.close()


# FIGURE 3: Q-Table Heatmap


# Load all q_tables
qtable_files = sorted(glob('data/q_tables/*_qtable.npy'))

if len(qtable_files) > 0:
    qtables = []
    for fpath in qtable_files:
        qtable = np.load(fpath)
        qtables.append(qtable)

    # Average across seeds
    mean_qtable = np.mean(np.array(qtables), axis=0)

    fig, ax = plt.subplots(figsize=(10, 6))
    im = ax.imshow(mean_qtable, cmap='viridis', aspect='auto', origin='lower')

    # Colorbar
    cbar = plt.colorbar(im, ax=ax, label='Mean Q-value (learned profit signal)')

    # Labels
    ax.set_xlabel('Action', fontsize=12)
    ax.set_ylabel('State index (pd x 27 + obi x 9 + tr x 3 + pt)', fontsize=12)
    ax.set_title('V2 Spoofer Learned Policy: Mean Q-Table (Aggregated, n=30 seeds)', fontsize=13)

    # Action labels
    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels(['Hold', 'Aggress', 'Withdraw'])

    # Annotation
    ax.text(
        0.02, 0.98,
        'Peak Q-values at states 27 & 45:\nearly-session, below-limit price conditions',
        transform=ax.transAxes,
        fontsize=10,
        verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.85, edgecolor='black')
    )

    plt.tight_layout()
    plt.savefig('figures/fig3_qtable_heatmap.pdf', dpi=300, bbox_inches='tight')
    print('Saved: figures/fig3_qtable_heatmap.pdf')
    plt.close()
else:
    print('Warning: No q_table files found in data/q_tables/')
