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

/* direct link costs from node 2 to others (classic DV lab topology) */
int connectcosts2[4] = { 3, 1, 0, 2 };

/* last distance vectors received from each neighbor (used for link changes) */
int neighbor_mincost2[4][4];

/* node 2 current minimum costs */
int mincost2[4];

struct distance_table
{
  int costs[4][4];
} dt2;

/* internal helpers (K&R style) */
static void sendmincost2();
static int recompute_mincost2();

/* students to write the following routines */

void rtinit2()
{
  int i, j;

  /* initialize distance table and saved neighbor vectors */
  for (i=0; i<4; i++) {
    for (j=0; j<4; j++) {
      dt2.costs[i][j] = INFINITY;
      neighbor_mincost2[i][j] = INFINITY;
    }
  }

  /* cost to self */
  dt2.costs[2][2] = 0;

  /* direct links (via the neighbor itself) */
  dt2.costs[0][0] = connectcosts2[0];
  dt2.costs[1][1] = connectcosts2[1];
  dt2.costs[3][3] = connectcosts2[3];

  /* initial mincost vector is just direct costs */
  for (i=0; i<4; i++)
    mincost2[i] = connectcosts2[i];

  if (TRACE > 0) {
    printf("\nrtinit2() called\n");
    printdt2(&dt2);
  }

  /* send initial distance vector to neighbors */
  sendmincost2();
}


void rtupdate2(rcvdpkt)
  struct rtpkt *rcvdpkt;
{
  int v, d;
  int changed;

  v = rcvdpkt->sourceid;

  /* record neighbor's latest vector */
  for (d=0; d<4; d++)
    neighbor_mincost2[v][d] = rcvdpkt->mincost[d];

  /* update our distance table column for 'via v' */
  for (d=0; d<4; d++) {
    if (connectcosts2[v] >= INFINITY || neighbor_mincost2[v][d] >= INFINITY)
      dt2.costs[d][v] = INFINITY;
    else
      dt2.costs[d][v] = connectcosts2[v] + neighbor_mincost2[v][d];
  }

  changed = recompute_mincost2();

  if (TRACE > 0) {
    printf("\nrtupdate2(): received a packet from %d\n", v);
    printdt2(&dt2);
  }

  if (changed)
    sendmincost2();
}


printdt2(dtptr)
  struct distance_table *dtptr;
{
  printf("                via     \n");
  printf("   D2 |    0     1    3 \n");
  printf("  ----|-----------------\n");
  printf("dest 0|  %3d   %3d   %3d\n",
         dtptr->costs[0][0], dtptr->costs[0][1], dtptr->costs[0][3]);
  printf("     1|  %3d   %3d   %3d\n",
         dtptr->costs[1][0], dtptr->costs[1][1], dtptr->costs[1][3]);
  printf("     3|  %3d   %3d   %3d\n",
         dtptr->costs[3][0], dtptr->costs[3][1], dtptr->costs[3][3]);
}


linkhandler2(linkid, newcost)
  int linkid, newcost;
{
  int d;
  int changed;

  /* update direct link cost */
  connectcosts2[linkid] = newcost;

  /* update direct-entry (dest=linkid via=linkid) */
  dt2.costs[linkid][linkid] = newcost;

  /* recompute all routes that go via this neighbor */
  for (d=0; d<4; d++) {
    if (newcost >= INFINITY || neighbor_mincost2[linkid][d] >= INFINITY)
      dt2.costs[d][linkid] = INFINITY;
    else
      dt2.costs[d][linkid] = newcost + neighbor_mincost2[linkid][d];
  }

  changed = recompute_mincost2();

  if (TRACE > 0) {
    printf("\nlinkhandler2(): link cost to %d changed to %d\n", linkid, newcost);
    printdt2(&dt2);
  }

  if (changed)
    sendmincost2();
}


/* ---------------- internal helper routines ---------------- */

static void sendmincost2()
{
  struct rtpkt pkt;
  int n;

  /* node 2 neighbors in classic topology: 0, 1, 3 */
  n = 0;
  if (connectcosts2[n] < INFINITY) {
    creatertpkt(&pkt, 2, n, mincost2);
    tolayer2(pkt);
  }

  n = 1;
  if (connectcosts2[n] < INFINITY) {
    creatertpkt(&pkt, 2, n, mincost2);
    tolayer2(pkt);
  }

  n = 3;
  if (connectcosts2[n] < INFINITY) {
    creatertpkt(&pkt, 2, n, mincost2);
    tolayer2(pkt);
  }
}


static int recompute_mincost2()
{
  int d, v;
  int old, best;
  int changed;

  changed = 0;

  for (d=0; d<4; d++) {
    old = mincost2[d];
    best = INFINITY;

    for (v=0; v<4; v++) {
      if (dt2.costs[d][v] < best)
        best = dt2.costs[d][v];
    }

    mincost2[d] = best;
    if (old != best)
      changed = 1;
  }

  return changed;
}
