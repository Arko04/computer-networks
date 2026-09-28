# HW4 – Distance-Vector Routing

An implementation of the **distributed, asynchronous distance-vector (Bellman-Ford) routing algorithm** for the 4-node network from Kurose & Ross. Each node keeps its own distance table, exchanges its minimum-cost vector only with direct neighbours, and recomputes routes as updates arrive. Link-cost changes are handled through `linkhandler*()`.

```
        1
   0 ------- 1
   | \       |
 7 |   \ 3   | 1
   |     \   |
   3 ------- 2
        2
```

| File | Description |
|------|-------------|
| `node0.c` … `node3.c` | My per-node routing logic: `rtinit`, `rtupdate`, `linkhandler` |
| `distance_vector.c` | Network emulator (course starter code, K&R C) |
| `Makefile` | Builds with `-std=gnu89`, which the legacy starter code needs |
| `output.txt` | Full trace of a run until convergence |
| `report.pdf` | Report (Persian) |

## Run

```bash
make run        # prompts for a trace level (0-2)
```
