# HW5 – ICMP Ping & Traceroute

`ping` and `traceroute` written from scratch with **raw ICMP sockets**. The code builds the ICMP header, computes the Internet checksum, and matches replies to requests. Written homework on routing algorithms (link-state vs. distance-vector, OSPF, BGP) is in the report.

| File | Description |
|------|-------------|
| `ping.py` | Sends an ICMP Echo Request once per second, matches the Echo Reply by packet ID, and prints the round-trip time (or a timeout) |
| `traceroute.py` | Sends probes with increasing TTL and prints each hop from the ICMP *Time Exceeded* replies |
| `screenshots/` | Code and test runs |
| `report.pdf` | Report (Persian) |

## Run

Raw sockets need administrator privileges:

```bash
sudo python3 ping.py
sudo python3 traceroute.py
```
