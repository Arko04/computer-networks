import matplotlib.pyplot as plt
import os

# --- CONFIGURATION ---
TRACE_DIR = "traces"        # Folder containing rtt_*.log files
OUTPUT_DIR = "graphs_final" # Folder to save the output image
RUN_ID = 1                  # We use Run #1 as the representative sample

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def plot_rtt_comparison():
    print("Generating RTT Comparison Timeline...")
    
    # Create the figure
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Define styles for each protocol
    # Reno: Blue Solid
    # Tahoe: Red Dashed
    # Vegas: Green Dotted
    styles = {
        'Reno':  {'color': '#003399', 'ls': '-',  'label': 'TCP Reno'},
        'Tahoe': {'color': '#CC0000', 'ls': '--', 'label': 'TCP Tahoe'},
        'Vegas': {'color': '#006600', 'ls': ':',  'label': 'TCP Vegas'}
    }

    protocols_found = False
    
    for proto in ['Reno', 'Tahoe', 'Vegas']:
        filename = f"{TRACE_DIR}/rtt_{proto}_{RUN_ID}.log"
        
        if not os.path.exists(filename):
            print(f"  Warning: {filename} not found. Skipping {proto}.")
            continue
            
        protocols_found = True
        
        # Read Data
        times = []
        rtts_flow1 = []
        
        try:
            with open(filename, 'r') as f:
                for line in f:
                    parts = line.split()
                    if len(parts) >= 3:
                        # Format: time rtt1 rtt2
                        t = float(parts[0])
                        # Convert Seconds to Milliseconds for readability
                        r1 = float(parts[1]) * 1000.0 
                        
                        times.append(t)
                        rtts_flow1.append(r1)
                        
            # Plot only Flow 1 for clarity (comparing protocols, not flows)
            ax.plot(times, rtts_flow1, 
                    label=styles[proto]['label'], 
                    color=styles[proto]['color'], 
                    linestyle=styles[proto]['ls'],
                    linewidth=2.5, 
                    alpha=0.8)
                    
        except Exception as e:
            print(f"  Error reading {proto}: {e}")

    if not protocols_found:
        print("Error: No RTT logs found. Please run ./run_project.sh first.")
        return

    # Formatting
    ax.set_title("RTT Comparison: Reno vs Tahoe vs Vegas", fontsize=18, fontweight='bold', pad=15)
    ax.set_ylabel("Round Trip Time (ms)", fontsize=14, fontweight='bold')
    ax.set_xlabel("Time (s)", fontsize=14, fontweight='bold')
    
    # Add Grid
    ax.grid(True, which='major', linestyle='-', alpha=0.6)
    ax.grid(True, which='minor', linestyle=':', alpha=0.3)
    ax.minorticks_on()
    
    # Legend
    ax.legend(fontsize=12, loc='best', framealpha=0.9, shadow=True)
    
    # Save
    save_path = f"{OUTPUT_DIR}/timeline_rtt_comparison.png"
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    print(f"Graph saved to: {save_path}")
    plt.close()

if __name__ == "__main__":
    plot_rtt_comparison()
