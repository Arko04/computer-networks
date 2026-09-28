# HW3 – Reliable Data Transfer

Transport-layer protocols that deliver data reliably over an unreliable channel. The channel is simulated and can **lose** and **corrupt** packets. The event-driven simulator is the Kurose & Ross RDT lab (Python version); the sender (A) and receiver (B) logic is mine.

| File | Protocol |
|------|----------|
| `rdtsim.py` | **Stop-and-wait (alternating-bit)**: checksums, ACK/NAK, sequence numbers and a retransmission timer |
| `bonus_go_back_n.py` | **Go-Back-N** (bonus): sliding window, cumulative ACKs, a single timer, and resending the whole window on timeout |
| `explanation.txt`, `bonus_explanation.txt` | Design notes and annotated sample runs |
| `report.pdf` | Full report (Persian) |

## Run

```bash
python3 rdtsim.py          -n 50 -d 200 -l 0.2 -c 0.2 -s 42 -v 2
python3 bonus_go_back_n.py -n 50 -d 200 -l 0.2 -c 0.2 -s 42 -v 2
```

`-n` messages, `-d` mean inter-arrival time, `-l` loss probability, `-c` corruption probability, `-s` seed, `-v` verbosity.

## Verification

Both protocols were run with 25% loss and 25% corruption across five seeds. In every run, all delivered messages reached the application **in order and without duplicates**. Stop-and-wait drops new application messages while it waits for an ACK, which the lab allows. Go-Back-N buffers them in its window, so it delivers almost every message.
