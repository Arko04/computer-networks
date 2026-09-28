# ===================================================================
# NS2 SIMULATION: ULTRA-PROFESSIONAL VERSION
# ===================================================================

if {$argc != 2} {
    puts "Usage: ns project_sim.tcl <Protocol> <Seed>"
    exit 1
}

set protocol [lindex $argv 0]
set seed [lindex $argv 1]

set ns [new Simulator]

# --- 1. RANDOM NUMBER GENERATION ---
# Stream 1: Link Delays (Float 5.0 - 25.0 ms)
set rng_delay [new RNG]
$rng_delay seed $seed
set rand_delay [new RandomVariable/Uniform]
$rand_delay use-rng $rng_delay
$rand_delay set min_ 5.0
$rand_delay set max_ 25.0

# Stream 2: Start Time Jitter (0.1s - 1.5s)
set rng_start [new RNG]
$rng_start seed [expr $seed + 99999] 
set rand_start [new RandomVariable/Uniform]
$rand_start use-rng $rng_start
$rand_start set min_ 0.1
$rand_start set max_ 1.5

set delay1_val [format "%.4f" [$rand_delay value]]
set delay2_val [format "%.4f" [$rand_delay value]]
set start1 [format "%.4f" [$rand_start value]]
set start2 [format "%.4f" [$rand_start value]]

# --- TRACING ---
set tf [open "out_${protocol}_${seed}.tr" w]
$ns trace-all $tf

# Separate RTT Log for Timeline Plotting
set rttfile [open "rtt_${protocol}_${seed}.log" w]

# --- 2. TOPOLOGY ---
set n0 [$ns node] ;# Src 1
set n1 [$ns node] ;# Src 2
set n2 [$ns node] ;# Router 1
set n3 [$ns node] ;# Router 2
set n4 [$ns node] ;# Dst 1
set n5 [$ns node] ;# Dst 2

$ns color 1 Blue
$ns color 2 Red

# [cite_start]Bottleneck: 100kbps, 1ms, Queue 10 [cite: 42-51]
$ns duplex-link $n0 $n2 100Mb 5ms DropTail
$ns duplex-link $n1 $n2 100Mb ${delay1_val}ms DropTail
$ns duplex-link $n2 $n3 100Kb 1ms DropTail
$ns queue-limit $n2 $n3 10
$ns queue-limit $n3 $n2 10
$ns duplex-link $n3 $n4 100Mb 5ms DropTail
$ns duplex-link $n3 $n5 100Mb ${delay2_val}ms DropTail

# Layout
$ns duplex-link-op $n0 $n2 orient right-down
$ns duplex-link-op $n1 $n2 orient right-up
$ns duplex-link-op $n2 $n3 orient right
$ns duplex-link-op $n3 $n4 orient right-up
$ns duplex-link-op $n3 $n5 orient right-down
$ns duplex-link-op $n2 $n3 queuePos 0.5

# --- 3. AGENTS & RTT MONITORING ---
proc attach-tcp-agent {node variant fid} {
    global ns
    if {$variant == "Reno"} { set tcp [new Agent/TCP/Reno] } \
    elseif {$variant == "Tahoe"} { set tcp [new Agent/TCP] } \
    elseif {$variant == "Vegas"} { set tcp [new Agent/TCP/Vegas] } \
    else { puts "Error: Unknown Protocol"; exit 1 }
    
    $tcp set class_ $fid
    $tcp set fid_ $fid
    $tcp set packetSize_ 1000
    $tcp set ttl_ 64
    $ns attach-agent $node $tcp
    return $tcp
}

set tcp1 [attach-tcp-agent $n0 $protocol 1]
set sink1 [new Agent/TCPSink]
$ns attach-agent $n4 $sink1
$ns connect $tcp1 $sink1
set ftp1 [new Application/FTP]
$ftp1 attach-agent $tcp1
$ns at $start1 "$ftp1 start"

set tcp2 [attach-tcp-agent $n1 $protocol 2]
set sink2 [new Agent/TCPSink]
$ns attach-agent $n5 $sink2
$ns connect $tcp2 $sink2
set ftp2 [new Application/FTP]
$ftp2 attach-agent $tcp2
$ns at $start2 "$ftp2 start"

# --- 4. RTT RECORDER FUNCTION ---
# This procedure runs every 0.5s to log the current RTT to a file
proc record_rtt {} {
    global ns tcp1 tcp2 rttfile
    set now [$ns now]
    # Get internal RTT variable (in seconds)
    set rtt1 [$tcp1 set rtt_]
    set rtt2 [$tcp2 set rtt_]
    puts $rttfile "$now $rtt1 $rtt2"
    $ns at [expr $now + 0.5] "record_rtt"
}

$ns at 0.1 "record_rtt"

# --- FINISH ---
proc finish {} {
    global ns tf rttfile
    $ns flush-trace
    close $tf
    close $rttfile
    exit 0
}

$ns at 1000.0 "finish"
$ns run