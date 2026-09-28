import matplotlib.pyplot as plt
import numpy as np
import csv
import os

# CONFIGURATION
INPUT_FILE = "results/all_runs_raw.csv"
OUTPUT_DIR = "graphs_final"

if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)

# 1. READ DATA
print(f"Reading {INPUT_FILE}...")
data = {} # Structure: {'Reno': {'Flow1': {'Thr':[], ...}, ...}, ...}

try:
    with open(INPUT_FILE, 'r') as f:
        reader = csv.DictReader(f)
        row_count = 0
        for row in reader:
            # Skip the 'AVERAGE' rows, we want the raw data to calculate our own stats
            if row['RunID'] == 'AVERAGE': continue
            
            p = row['Protocol']
            f = row['Flow']
            
            if p not in data: data[p] = {}
            if f not in data[p]: data[p][f] = {'Thr': [], 'RTT': [], 'Loss': []}
            
            # Safe Float Conversion
            try:
                data[p][f]['Thr'].append(float(row['Throughput_Kbps']))
                data[p][f]['RTT'].append(float(row['RTT_ms']))
                data[p][f]['Loss'].append(float(row['Loss_Pct']))
                row_count += 1
            except ValueError: continue

    if row_count == 0:
        print("ERROR: CSV file is empty or formatted incorrectly!")
        exit()
    print(f"Successfully loaded {row_count} data points.")

except FileNotFoundError:
    print("ERROR: results/all_runs_raw.csv not found. Run ./run_project.sh first!")
    exit()

# 2. PLOTTING FUNCTION
def plot_metric(metric, title, ylabel, filename, ylim=None):
    protocols = ['Reno', 'Tahoe', 'Vegas']
    
    # Prepare Means and Standard Deviations
    means1, stds1 = [], []
    means2, stds2 = [], []
    
    for p in protocols:
        if p in data:
            v1 = data[p]['Flow1'][metric]
            v2 = data[p]['Flow2'][metric]
            means1.append(np.mean(v1))
            stds1.append(np.std(v1))
            means2.append(np.mean(v2))
            stds2.append(np.std(v2))
        else:
            means1.append(0); stds1.append(0)
            means2.append(0); stds2.append(0)

    # Plot Setup
    x = np.arange(len(protocols))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # High Contrast Bars
    # Flow 1 = Dark Blue, Flow 2 = Dark Red
    rects1 = ax.bar(x - width/2, means1, width, yerr=stds1, capsize=8, 
                    label='Flow 1', color='#104E8B', edgecolor='black', alpha=0.9)
    rects2 = ax.bar(x + width/2, means2, width, yerr=stds2, capsize=8, 
                    label='Flow 2', color='#8B0000', edgecolor='black', alpha=0.9)

    # Styling
    ax.set_ylabel(ylabel, fontsize=14, fontweight='bold')
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(protocols, fontsize=14)
    ax.legend(fontsize=12, loc='best', framealpha=1, shadow=True)
    ax.grid(axis='y', linestyle='--', alpha=0.5, color='gray')
    
    if ylim: ax.set_ylim(0, ylim)

    # Add numeric labels on top
    ax.bar_label(rects1, padding=3, fmt='%.1f', fontsize=11, fontweight='bold')
    ax.bar_label(rects2, padding=3, fmt='%.1f', fontsize=11, fontweight='bold')

    plt.tight_layout()
    save_path = f"{OUTPUT_DIR}/{filename}"
    plt.savefig(save_path, dpi=300)
    print(f"Saved: {save_path}")
    plt.close()

# 3. GENERATE CHARTS
plot_metric('Thr', 'Average Throughput Comparison', 'Throughput (Kbps)', 'chart_throughput.png')
plot_metric('Loss', 'Packet Loss Rate Comparison', 'Packet Loss (%)', 'chart_loss.png', ylim=15)
plot_metric('RTT', 'Round Trip Time Comparison', 'RTT (ms)', 'chart_rtt.png')