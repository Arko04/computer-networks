import matplotlib.pyplot as plt
import numpy as np
import os

# --- CONFIGURATION ---
TRACE_DIR = "traces"
OUTPUT_DIR = "graphs_final"
RUN_ID = 1
TOTAL_TIME = 1000
NUM_POINTS = 10
BIN_SIZE = TOTAL_TIME / NUM_POINTS  # 100 seconds per point
FLOW_ID_TO_PLOT = 1  # We compare Flow 1 only to see the dynamics

if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)

# Styles: Distinct colors and markers
STYLES = {
    'Reno':  {'c': '#003399', 'ls': '-',  'marker': 'o', 'label': 'Reno (Flow 1)'},
    'Tahoe': {'c': '#CC0000', 'ls': '--', 'marker': 's', 'label': 'Tahoe (Flow 1)'},
    'Vegas': {'c': '#006600', 'ls': ':',  'marker': '^', 'label': 'Vegas (Flow 1)'}
}

# X-axis: 50, 150, 250...
X_AXIS = np.arange(BIN_SIZE/2, TOTAL_TIME, BIN_SIZE)

def get_binned_flow_throughput(proto):
    print(f"--- Processing {proto} ---")
    filename = f"{TRACE_DIR}/out_{proto}_{RUN_ID}.tr"
    if not os.path.exists(filename):
        print(f"File not found: {filename}")
        return None

    bins = np.zeros(NUM_POINTS)
    
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('r'):
                p = line.split()
                try:
                    time = float(p[1])
                    to_node = int(p[3])
                    size = int(p[5])
                    fid = int(p[7])
                    
                    # LOGIC: Check strict destination and Flow ID
                    # Flow 1 goes to Node 4
                    if size > 100 and fid == FLOW_ID_TO_PLOT and to_node == 4:
                        bin_idx = int(time / BIN_SIZE)
                        if bin_idx < NUM_POINTS:
                            bins[bin_idx] += size
                except: pass

    # Convert to Kbps
    kbps_bins = (bins * 8) / (BIN_SIZE * 1000.0)
    
    # Print values to console for verification
    print(f"  Values: {np.round(kbps_bins, 2)} Kbps")
    return kbps_bins

def get_binned_rtt(proto):
    filename = f"{TRACE_DIR}/rtt_{proto}_{RUN_ID}.log"
    if not os.path.exists(filename): return None

    bin_samples = [[] for _ in range(NUM_POINTS)]

    with open(filename, 'r') as f:
        for line in f:
            p = line.split()
            if len(p) >= 2:
                time = float(p[0])
                # Use RTT of Flow 1 only (Column 1 is Time, Col 2 is Flow1, Col 3 is Flow2)
                rtt_ms = float(p[1]) * 1000.0
                
                bin_idx = int(time / BIN_SIZE)
                if bin_idx < NUM_POINTS:
                    bin_samples[bin_idx].append(rtt_ms)

    final_rtt = []
    for samples in bin_samples:
        if samples: final_rtt.append(np.mean(samples))
        else: final_rtt.append(0)
    return final_rtt

# --- PLOTTING ---
def plot_graph(data_dict, title, ylabel, filename, ylim_min=None, ylim_max=None):
    fig, ax = plt.subplots(figsize=(12, 7))
    
    for proto, y_values in data_dict.items():
        if y_values is not None:
            s = STYLES[proto]
            ax.plot(X_AXIS, y_values, label=s['label'], color=s['c'], 
                    linestyle=s['ls'], marker=s['marker'], 
                    linewidth=2.5, markersize=10, alpha=0.8)

    # Reference Line for Fair Share (50 Kbps)
    if "Throughput" in title:
        ax.axhline(50, color='gray', lw=2, linestyle='--', alpha=0.5)
        ax.text(0, 51, ' Fair Share (50Kb)', color='gray', fontweight='bold')

    ax.set_title(title, fontsize=18, fontweight='bold', pad=15)
    ax.set_ylabel(ylabel, fontsize=14, fontweight='bold')
    ax.set_xlabel("Time (s)", fontsize=14, fontweight='bold')
    
    # Smart Y-Limit to zoom in on the action
    if ylim_min is not None and ylim_max is not None:
        ax.set_ylim(ylim_min, ylim_max)
    
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend(fontsize=12, framealpha=1, shadow=True)
    
    plt.tight_layout()
    save_path = f"{OUTPUT_DIR}/{filename}"
    plt.savefig(save_path, dpi=300)
    print(f"Saved Graph: {save_path}")
    plt.close()

# --- EXECUTION ---
thr_data = {}
rtt_data = {}

for p in ['Reno', 'Tahoe', 'Vegas']:
    thr_data[p] = get_binned_flow_throughput(p)
    rtt_data[p] = get_binned_rtt(p)

# 1. Plot Throughput (Zoomed in to 40-60 to see oscillations)
plot_graph(thr_data, 
           "Flow 1 Throughput Stability (10-Point Avg)", 
           "Throughput (Kbps)", 
           "compare_flow1_throughput.png",
           ylim_min=40, ylim_max=60)

# 2. Plot RTT
plot_graph(rtt_data, 
           "Flow 1 RTT Latency (10-Point Avg)", 
           "RTT (ms)", 
           "compare_flow1_rtt.png")