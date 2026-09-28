# Computer Networks

Coursework for **Computer Networks** at the University of Tehran, Faculty of Electrical and Computer Engineering (Fall 2025). The course follows Kurose & Ross, *Computer Networking: A Top-Down Approach*.

The assignments go down the protocol stack. They implement an HTTP server, reliable transport protocols, a distance-vector routing protocol, and ICMP tools, and finish with an NS2 study of TCP congestion control.

## Projects

| # | Topic | What I built | Tech |
|---|-------|--------------|------|
| HW1 | [Network fundamentals & Wireshark](hw1-network-fundamentals-wireshark/) | Packet vs. circuit switching, end-to-end delay and throughput; Wireshark packet-capture lab | Wireshark |
| HW2 | [HTTP web server](hw2-http-web-server/) | A web server built on raw TCP sockets (single-threaded and multithreaded) and an HTTP client | Python, sockets, threading |
| HW3 | [Reliable data transfer](hw3-reliable-data-transfer/) | **stop-and-wait (alternating-bit, ACK/NAK)** and **Go-Back-N** senders/receivers over a lossy, corrupting simulated channel | Python |
| HW4 | [Distance-vector routing](hw4-distance-vector-routing/) | A distributed, asynchronous **Bellman-Ford** routing protocol for a 4-node network, including link-cost changes | C |
| HW5 | [ICMP ping & traceroute](hw5-icmp-ping-traceroute/) | `ping` and `traceroute` built from scratch with raw ICMP sockets | Python, raw sockets |
| HW6 | [Link layer](hw6-link-layer/) | ARP, MAC vs. IP addressing across subnets, CRC, CSMA | — |
| CA1 | [P4 learning switch](ca1-p4-learning-switch/) | Set up a P4 / Mininet environment and a layer-2 learning switch (report) | P4, Mininet |
| CA2 | [TCP congestion control in NS2](ca2-ns2-tcp-congestion-control/) | A dumbbell-topology simulation comparing **TCP Reno, Tahoe and Vegas** over 10 randomised runs each | NS2 (Tcl), AWK, Bash, Python |

There's also [lecture-notes/](lecture-notes/): my own notes for every lecture of the semester (in Persian), named by date on the Solar Hijri calendar.

## Verified

| Project | Check |
|---------|-------|
| HW2 | Both servers return `200` for an existing file and `404` for a missing one; the multithreaded server handles parallel requests |
| HW3 | Stress-tested with 25% loss and 25% corruption over 5 seeds: every delivered message arrives in order with no duplicates |
| HW4 | Builds with `make` and converges to correct shortest-path tables (`output.txt`) |
| CA2 | `plot_summary_charts.py` regenerates the charts from `results/all_runs_raw.csv` |

## Team

CA1 and CA2 were done with **Amirhossein Mansouri**. The homework assignments are individual.
