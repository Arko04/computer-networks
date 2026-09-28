import matplotlib.pyplot as plt
import os

TRACE_DIR = "traces"
OUTPUT_DIR = "graphs_final"
RUN_ID = 1
INTERVAL = 5.0  # Smoothing bucket (seconds)

if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)

# Configuration: Which Node is the Destination for which Flow?
# Flow 1 -> Node 4
# Flow 2 -> Node 5
DEST_NODES = {1: 4, 2: 5}

def get_throughput(protocol):
    filename = f"{TRACE_DIR}/out_{protocol}_{RUN_ID}.tr"
    if not os.path.exists(filename):
        print(f"Warning: {filename} missing. Skipping.")
        return None

    print(f"Parsing {protocol} trace...")
    buckets = {1: {}, 2: {}}
    
    with open(filename, 'r') as f:
        for line in f:
            # We only care about Receive (r) events
            if line.startswith('r'): 
                p = line.split()
                try:
                    # Parse Trace Line
                    # Format: event time from to pkt_type size flags fid ...
                    time = float(p[1])
                    to_node = int(p[3])  # <--- CRITICAL FIX: Identify Receiver
                    size = int(p[5])
                    fid = int(p[7])
                    
                    # 1. Filter: Must be a Data Packet (size > 100)
                    # 2. Filter: Must be received AT THE DESTINATION NODE
                    if size > 100 and fid in DEST_NODES and to_node == DEST_NODES[fid]:
                        idx = int(time / INTERVAL)
                        buckets[fid][idx] = buckets[fid].get(idx, 0) + size
                except (ValueError, IndexError): 
                    pass

    # Convert buckets to X, Y lists
    data = {}
    for fid in [1, 2]:
        x, y = [], []
        if fid in buckets:
            # Sort by time
            for i in sorted(buckets[fid].keys()):
                x.append(i * INTERVAL)
                # Formula: (Bytes * 8) / (1000 * Seconds) = Kbps
                kbps = buckets[fid][i] * 8 / (1000.0 * INTERVAL)
                y.append(kbps)
        data[fid] = (x, y)
    return data

def plot_single_protocol(proto, data):
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot Flow 1 (Blue) & Flow 2 (Red)
    if data[1][0]: # Check if data exists
        ax.plot(data[1][0], data[1][1], label='Flow 1', color='#003399', lw=2)
    if data[2][0]:
        ax.plot(data[2][0], data[2][1], label='Flow 2', color='#CC0000', lw=2, alpha=0.8)

    ax.set_title(f"Throughput: TCP {proto}", fontsize=16, fontweight='bold')
    ax.set_ylabel("Throughput (Kbps)", fontsize=14)
    ax.set_xlabel("Time (s)", fontsize=14)
    
    # Y-Axis Limit: Slightly above 100Kbps
    ax.set_ylim(0, 120)
    
    # Reference Line at 100 Kbps
    ax.axhline(100, color='black', lw=2, linestyle='-', alpha=0.5)
    ax.text(0, 102, ' Max Capacity (100Kb)', fontweight='bold')
    
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend(fontsize=12, loc='lower right')
    
    outfile = f"{OUTPUT_DIR}/timeline_{proto}.png"
    plt.savefig(outfile, dpi=300)
    print(f"Saved {outfile}")
    plt.close()

# --- MAIN EXECUTION ---
all_data = {}
for p in ['Reno', 'Tahoe', 'Vegas']:
    d = get_throughput(p)
    if d:
        plot_single_protocol(p, d)
        all_data[p] = d

# Plot Combined Comparison (Flow 1 Only)
if all_data:
    print("Generating Combined Comparison...")
    fig, ax = plt.subplots(figsize=(16, 8))
    
    colors = {'Reno': '#003399', 'Tahoe': '#CC0000', 'Vegas': '#006600'}
    styles = {'Reno': '-', 'Tahoe': '--', 'Vegas': '-.'}

    for p, d in all_data.items():
        if d[1][0]: # Check if Flow 1 has data
            ax.plot(d[1][0], d[1][1], label=f'{p}', 
                    color=colors[p], linestyle=styles[p], lw=2.5)

    ax.set_title("Protocol Comparison (Flow 1)", fontsize=18, fontweight='bold')
    ax.set_ylabel("Throughput (Kbps)", fontsize=14)
    ax.set_xlabel("Time (s)", fontsize=14)
    ax.set_ylim(0, 120)
    ax.legend(fontsize=14)
    ax.grid(True, alpha=0.4)
    
    # Reference Line
    ax.axhline(100, color='black', lw=2, linestyle='-', alpha=0.5)
    ax.text(0, 102, ' Max Capacity (100Kb)', fontweight='bold')

    plt.savefig(f"{OUTPUT_DIR}/timeline_ALL_COMPARED.png", dpi=300)
    print("Saved timeline_ALL_COMPARED.png")