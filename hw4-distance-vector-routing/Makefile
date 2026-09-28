# The simulator (distance_vector.c) is the K&R-style C starter code from
# Kurose & Ross, so it must be compiled as gnu89.
CC      ?= cc
CFLAGS  ?= -std=gnu89 -w -Wno-error=return-mismatch
SRCS     = distance_vector.c node0.c node1.c node2.c node3.c

dv: $(SRCS)
	$(CC) $(CFLAGS) -o $@ $(SRCS)

run: dv
	./dv

clean:
	rm -f dv a.out

.PHONY: run clean
