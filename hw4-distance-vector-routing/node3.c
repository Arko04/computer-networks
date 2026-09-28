#include <stdio.h>

#define INFINITY 999

struct rtpkt {
  int sourceid;
  int destid;
  int mincost[4];
};

extern int TRACE;
extern int YES;
extern int NO;

extern void tolayer2();
extern void creatertpkt();

/*
 * Node 3 direct link costs (from the topology figure in Q11):
 * 3-0 cost 7, 3-2 cost 2, no direct link to 1, cost to self 0
 */
int connectcosts3[4] = { 7, INFINITY, 2, 0 };

/* store last mincost vectors received from neighbors (helps if link changes existed) */
int neighbor_mincost3[4][4];

/* node 3 current minimum costs */
int mincost3[4];

struct distance_table
{
  int costs[4][4];
} dt3;

/* internal helpers */
static void sendmincost3();
static int recompute_mincost3();

/* ------------ required routines ------------ */

void rtinit3()
{
  int i, j;

  /* init distance table and neighbor vectors */
  for (i = 0; i < 4; i++) {
    for (j = 0; j < 4; j++) {
      dt3.costs[i][j] = INFINITY;
      neighbor_mincost3[i][j] = INFINITY;
    }
  }

  /* cost to self */
  dt3.costs[3][3] = 0;

  /* direct links (via the neighbor itself) */
  dt3.costs[0][0] = connectcosts3[0];
  dt3.costs[2][2] = connectcosts3[2];

  /* initial mincost is direct costs */
  for (i = 0; i < 4; i++)
    mincost3[i] = connectcosts3[i];

  if (TRACE > 0) {
    printf("\nrtinit3() called\n");
    printdt3(&dt3);
  }

  sendmincost3();
}


void rtupdate3(rcvdpkt)
  struct rtpkt *rcvdpkt;
{
  int v, d;
  int changed;

  v = rcvdpkt->sourceid;

  /* remember neighbor's advertised vector */
  for (d = 0; d < 4; d++)
    neighbor_mincost3[v][d] = rcvdpkt->mincost[d];

  /* update our costs to each destination via neighbor v */
  for (d = 0; d < 4; d++) {
    if (connectcosts3[v] >= INFINITY || neighbor_mincost3[v][d] >= INFINITY)
      dt3.costs[d][v] = INFINITY;
    else
      dt3.costs[d][v] = connectcosts3[v] + neighbor_mincost3[v][d];
  }

  changed = recompute_mincost3();

  if (TRACE > 0) {
    printf("\nrtupdate3(): received a packet from %d\n", v);
    printdt3(&dt3);
  }

  if (changed)
    sendmincost3();
}


/* pretty-print for node 3 (like the standard DV lab style) */
printdt3(dtptr)
  struct distance_table *dtptr;
{
  printf("                via     \n");
  printf("   D3 |    0     2 \n");
  printf("  ----|-------------\n");
  printf("dest 0|  %3d   %3d\n", dtptr->costs[0][0], dtptr->costs[0][2]);
  printf("     1|  %3d   %3d\n", dtptr->costs[1][0], dtptr->costs[1][2]);
  printf("     2|  %3d   %3d\n", dtptr->costs[2][0], dtptr->costs[2][2]);
}


/*
 * NOTE: Bonus link-change handlers are required only for node0 and node1 per the PDF.
 * This stub is here just in case your simulator expects it; it will never be called
 * unless LINKCHANGES includes node3 in your environment.
 */
linkhandler3(linkid, newcost)
  int linkid, newcost;
{
  if (TRACE > 0) {
    printf("\nlinkhandler3(): called (unexpected in this HW). linkid=%d newcost=%d\n",
           linkid, newcost);
  }
}


/* ------------ internal helper routines ------------ */

static void sendmincost3()
{
  struct rtpkt pkt;

  /* node 3 neighbors are 0 and 2 */
  if (connectcosts3[0] < INFINITY) {
    creatertpkt(&pkt, 3, 0, mincost3);
    tolayer2(pkt);
  }

  if (connectcosts3[2] < INFINITY) {
    creatertpkt(&pkt, 3, 2, mincost3);
    tolayer2(pkt);
  }
}


static int recompute_mincost3()
{
  int d, v;
  int old, best;
  int changed;

  changed = 0;

  for (d = 0; d < 4; d++) {
    old = mincost3[d];
    best = INFINITY;

    for (v = 0; v < 4; v++) {
      if (dt3.costs[d][v] < best)
        best = dt3.costs[d][v];
    }

    mincost3[d] = best;
    if (old != best)
      changed = 1;
  }

  return changed;
}
