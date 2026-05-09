import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def load_tape_data():
    # Load tapes from specific directory structure
    baseline_files = glob.glob('data/treatment_v1/baseline_seed*_tape.csv')
    v1_files = glob.glob('data/treatment_v1/treatment_seed*_tape.csv')
    v2_files = glob.glob('data/treatment_v2/treatment_v2_seed*_tape.csv')

    file_counts = {
        'baseline': len(baseline_files),
        'treatment': len(v1_files),
        'treatment_v2': len(v2_files)
    }

    all_data = []
    for f in baseline_files:
        try:
            df = pd.read_csv(f, header=None, names=['type', 'time', 'price'], on_bad_lines='skip')
            df = df[df['type'].str.strip() == 'TRD']
            df['price'] = pd.to_numeric(df['price'])
            df['time'] = pd.to_numeric(df['time'])
            df['condition'] = 'baseline'
            all_data.append(df)
        except Exception as e:
            continue

    for f in v1_files:
        try:
            df = pd.read_csv(f, header=None, names=['type', 'time', 'price'], on_bad_lines='skip')
            df = df[df['type'].str.strip() == 'TRD']
            df['price'] = pd.to_numeric(df['price'])
            df['time'] = pd.to_numeric(df['time'])
            df['condition'] = 'treatment'
            all_data.append(df)
        except Exception as e:
            continue

    for f in v2_files:
        try:
            df = pd.read_csv(f, header=None, names=['type', 'time', 'price'], on_bad_lines='skip')
            df = df[df['type'].str.strip() == 'TRD']
            df['price'] = pd.to_numeric(df['price'])
            df['time'] = pd.to_numeric(df['time'])
            df['condition'] = 'treatment_v2'
            all_data.append(df)
        except Exception as e:
            continue

    if not all_data: return pd.DataFrame()

    full_data = pd.concat(all_data, ignore_index=True)

    # Print file counts
    print(f"Baseline files found: {file_counts['baseline']}")
    print(f"V1 files found: {file_counts['treatment']}")
    print(f"V2 files found: {file_counts['treatment_v2']}")

    # Print last trade timestamp per condition
    last_times = {}
    for cond in ['baseline', 'treatment', 'treatment_v2']:
        cond_data = full_data[full_data['condition'] == cond]
        if not cond_data.empty:
            last_times[cond] = int(cond_data['time'].max())
        else:
            last_times[cond] = None

    print(f"Last trade timestamp per condition: baseline={last_times['baseline']}, v1={last_times['treatment']}, v2={last_times['treatment_v2']}")

    return full_data


def plot_adaptation(df):
    if df.empty: return

    # Extract seed numbers from tape filenames to count unique seeds per bin
    # For now, we'll track data availability by counting rows per condition-bin
    bins = [0, 100, 200, 300, 400, 500, 600]
    labels = [50, 150, 250, 350, 450, 550]  # Midpoints for plotting
    df['time_bin'] = pd.cut(df['time'], bins=bins, labels=labels)

    # Calculate Mean, Standard Error, and count unique seeds per condition-bin
    agg_df = df.groupby(['condition', 'time_bin'], observed=True).agg(
        mean=('price', 'mean'),
        sem=('price', 'sem'),
        n_seeds=('price', 'count')  # Count of data points (proxy for activity)
    ).reset_index()

    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rcParams.update({'font.size': 12})
    fig, ax = plt.subplots(figsize=(10, 6))

    colors = {'baseline': 'gray', 'treatment': '#E05C5C', 'treatment_v2': '#5B8DD9'}
    cond_labels = {'baseline': 'Baseline', 'treatment': 'V1 (Heuristic)', 'treatment_v2': 'V2 (Q-Learning)'}

    # Track sparse bins (450 and 550 time points)
    sparse_markers = []

    for cond in ['baseline', 'treatment', 'treatment_v2']:
        cond_data = agg_df[agg_df['condition'] == cond].copy()

        # Plot all available points
        valid_data = cond_data.dropna(subset=['mean', 'sem'])
        if valid_data.empty: continue

        ax.plot(valid_data['time_bin'].astype(float), valid_data['mean'],
                color=colors[cond], label=cond_labels[cond], linewidth=2.5, marker='o')
        ax.fill_between(valid_data['time_bin'].astype(float),
                        valid_data['mean'] - valid_data['sem'],
                        valid_data['mean'] + valid_data['sem'],
                        color=colors[cond], alpha=0.2)

        # Check for sparse data in bins 5 and 6 (450 and 550)
        for time_bin in [450, 550]:
            bin_data = cond_data[cond_data['time_bin'] == time_bin]
            if not bin_data.empty and bin_data['n_seeds'].values[0] < 5:
                sparse_markers.append((time_bin, bin_data['mean'].values[0], cond))

    ax.set_title("ZIP Buyer Adaptation Under Spoofing Attack (n=30 seeds)", fontsize=14, weight='bold')
    ax.set_xlabel("Session time (seconds)", fontsize=12)
    ax.set_ylabel("Mean transaction price (£)", fontsize=12)

    # Set x-axis to show all 6 bins
    ax.set_xticks([50, 150, 250, 350, 450, 550])

    ax.axvline(x=200, color='black', linestyle='--', alpha=0.5)
    ax.axvline(x=400, color='black', linestyle='--', alpha=0.5)

    ax.text(200, ax.get_ylim()[1] * 0.98, " Early | Mid", verticalalignment='top')
    ax.text(400, ax.get_ylim()[1] * 0.98, " Mid | Late", verticalalignment='top')

    # Add sparse data annotations
    if sparse_markers:
        for x, y, cond in sparse_markers:
            ax.annotate('sparse data', xy=(x, y), xytext=(5, 10),
                       textcoords='offset points', fontsize=9, style='italic',
                       color=colors[cond], alpha=0.7)

    ax.annotate('Market activity ceases\n(no trades recorded)',
                xy=(420, 81.5),
                fontsize=10,
                color='#666666',
                ha='center',
                style='italic')

    # Add small vertical markers showing last trade time
    ax.axvline(x=373, color='#E05C5C', linewidth=1,
               linestyle=':', alpha=0.7)
    ax.axvline(x=236, color='#5B8DD9', linewidth=1,
               linestyle=':', alpha=0.7)
    ax.text(373, 80.3, 'V1 last\ntrade', color='#E05C5C',
            fontsize=8, ha='center')
    ax.text(236, 80.3, 'V2 last\ntrade', color='#5B8DD9',
            fontsize=8, ha='center')

    ax.legend(loc='lower left')

    os.makedirs('figures', exist_ok=True)
    plt.tight_layout()
    plt.savefig('figures/fig4_zip_adaptation.pdf', dpi=300)
    print("Saved: figures/fig4_zip_adaptation.pdf")


if __name__ == '__main__':
    data = load_tape_data()
    plot_adaptation(data)