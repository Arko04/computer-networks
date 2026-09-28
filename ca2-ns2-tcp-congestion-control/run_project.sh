#!/bin/bash

# =================================================================
# NS2 SIMULATION MANAGER - DETAILED LOGGING EDITION
# =================================================================

# 1. Setup Directories
echo "[INIT] Cleaning old files..."
rm -rf traces results
mkdir -p traces results
mkdir -p results/raw_data

# 2. Initialize CSV Header
echo "Protocol,Flow,RunID,Throughput_Kbps,RTT_ms,Loss_Pct" > results/all_runs_raw.csv

protocols=("Reno" "Tahoe" "Vegas")

echo "================================================="
echo "   STARTING SIMULATION SUITE"
echo "   Time: $(date)"
echo "================================================="

for proto in "${protocols[@]}"; do
    echo ""
    echo "-------------------------------------------------"
    echo "[$(date +%H:%M:%S)] Processing Protocol: $proto"
    echo "-------------------------------------------------"
    
    # Reset Accumulators
    sum_thr1=0; sum_thr2=0
    sum_loss1=0; sum_loss2=0
    sum_rtt1=0; sum_rtt2=0
    
    for i in {1..10}; do
        echo -n "  [Run $i/10] Simulating... "
        
        # Run NS2 (Capture execution time)
        start_t=$(date +%s%N)
        ns project_sim.tcl $proto $i > /dev/null 2>&1
        end_t=$(date +%s%N)
        dur=$(( (end_t - start_t) / 1000000 )) # Convert ns to ms
        
        echo "Done (${dur}ms). Parsing data..."
        
        trace="out_${proto}_${i}.tr"
        rttlog="rtt_${proto}_${i}.log"
        
        # Check if trace exists
        if [ ! -f "$trace" ]; then
            echo "    [ERROR] Trace file $trace not found! Skipping..."
            continue
        fi
        
        # --- 1. THROUGHPUT CALCULATION ---
        thr1=$(awk -v dest=4 -v fid=1 '$1=="r" && $4==dest && $8==fid {sum+=$6} END {if(sum>0) print sum*8/1000/1000; else print 0}' $trace)
        thr2=$(awk -v dest=5 -v fid=2 '$1=="r" && $4==dest && $8==fid {sum+=$6} END {if(sum>0) print sum*8/1000/1000; else print 0}' $trace)
        
        # --- 2. PACKET LOSS CALCULATION ---
        s1=$(awk '$1=="+" && $3==0 && $8==1 {n++} END {print n+0}' $trace)
        r1=$(awk '$1=="r" && $4==4 && $8==1 {n++} END {print n+0}' $trace)
        if [ "$s1" -gt 0 ]; then l1=$(echo "scale=4; ($s1-$r1)/$s1*100" | bc); else l1=0; fi

        s2=$(awk '$1=="+" && $3==1 && $8==2 {n++} END {print n+0}' $trace)
        r2=$(awk '$1=="r" && $4==5 && $8==2 {n++} END {print n+0}' $trace)
        if [ "$s2" -gt 0 ]; then l2=$(echo "scale=4; ($s2-$r2)/$s2*100" | bc); else l2=0; fi
        
        # --- 3. RTT CALCULATION ---
        rtt1=$(awk -f rtt.awk -v fsrc=0 -v fdst=4 $trace)
        rtt2=$(awk -f rtt.awk -v fsrc=1 -v fdst=5 $trace)
        
        # --- LOGGING TO CONSOLE ---
        echo "      -> Flow 1: Thr=$thr1 Kbps | Loss=$l1 % | RTT=$rtt1 ms"
        echo "      -> Flow 2: Thr=$thr2 Kbps | Loss=$l2 % | RTT=$rtt2 ms"
        
        # SAVE TO CSV
        echo "$proto,Flow1,$i,$thr1,$rtt1,$l1" >> results/all_runs_raw.csv
        echo "$proto,Flow2,$i,$thr2,$rtt2,$l2" >> results/all_runs_raw.csv
        
        # ACCUMULATE SUMS (Using BC for floats)
        sum_thr1=$(echo "$sum_thr1 + $thr1" | bc); sum_thr2=$(echo "$sum_thr2 + $thr2" | bc)
        sum_loss1=$(echo "$sum_loss1 + $l1" | bc); sum_loss2=$(echo "$sum_loss2 + $l2" | bc)
        sum_rtt1=$(echo "$sum_rtt1 + $rtt1" | bc); sum_rtt2=$(echo "$sum_rtt2 + $rtt2" | bc)
        
        # CLEANUP (Keep Run #1 for graphs)
        if [ "$i" -eq 1 ]; then
            mv $trace traces/
            mv $rttlog traces/
            echo "      [Info] Trace files saved for timeline plotting."
        else
            rm $trace
            rm $rttlog
        fi
    done
    
    # --- AVERAGING ---
    echo "  [Stats] Calculating averages for $proto..."
    avg_t1=$(echo "scale=2; $sum_thr1/10"|bc); avg_t2=$(echo "scale=2; $sum_thr2/10"|bc)
    avg_l1=$(echo "scale=2; $sum_loss1/10"|bc); avg_l2=$(echo "scale=2; $sum_loss2/10"|bc)
    avg_r1=$(echo "scale=2; $sum_rtt1/10"|bc); avg_r2=$(echo "scale=2; $sum_rtt2/10"|bc)
    
    echo "  [FINAL] $proto Results:"
    echo "    Flow 1 Avg: $avg_t1 Kbps, $avg_l1 %, $avg_r1 ms"
    echo "    Flow 2 Avg: $avg_t2 Kbps, $avg_l2 %, $avg_r2 ms"
    
    # APPEND AVERAGE ROW TO CSV
    echo "$proto,Flow1,AVERAGE,$avg_t1,$avg_r1,$avg_l1" >> results/all_runs_raw.csv
    echo "$proto,Flow2,AVERAGE,$avg_t2,$avg_r2,$avg_l2" >> results/all_runs_raw.csv
done

echo ""
echo "================================================="
echo "   COMPLETE! Data saved to results/all_runs_raw.csv"
echo "================================================="