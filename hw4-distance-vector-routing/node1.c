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

/* direct link costs from node 1 to others (classic DV lab topology) */
int connectcosts1[4] = { 1, 0, 1, INFINITY };

/* last distance vectors received from each neighbor (used for link changes) */
int neighbor_mincost1[4][4];

/* node 1 current minimum costs */
int mincost1[4];

struct distance_table
{
  int costs[4][4];
} dt1;

/* internal helpers (K&R style) */
static void sendmincost1();
static int recompute_mincost1();

/* students to write the following routines */

void rtinit1()
{
  int i, j;

  /* initialize distance table and saved neighbor vectors */
  for (i=0; i<4; i++) {
    for (j=0; j<4; j++) {
      dt1.costs[i][j] = INFINITY;
      neighbor_mincost1[i][j] = INFINITY;
    }
  }

  /* cost to self */
  dt1.costs[1][1] = 0;

  /* direct links (via the neighbor itself) */
  dt1.costs[0][0] = connectcosts1[0];
  dt1.costs[2][2] = connectcosts1[2];
  dt1.costs[3][3] = connectcosts1[3];

  /* initial mincost vector is just direct costs */
  for (i=0; i<4; i++)
    mincost1[i] = connectcosts1[i];

  if (TRACE > 0) {
    printf("\nrtinit1() called\n");
    printdt1(&dt1);
  }

  /* send initial distance vector to neighbors */
  sendmincost1();
}


void rtupdate1(rcvdpkt)
  struct rtpkt *rcvdpkt;
{
  int v, d;
  int changed;

  v = rcvdpkt->sourceid;

  /* record neighbor's latest vector */
  for (d=0; d<4; d++)
    neighbor_mincost1[v][d] = rcvdpkt->mincost[d];

  /* update our distance table column for 'via v' */
  for (d=0; d<4; d++) {
    if (connectcosts1[v] >= INFINITY || neighbor_mincost1[v][d] >= INFINITY)
      dt1.costs[d][v] = INFINITY;
    else
      dt1.costs[d][v] = connectcosts1[v] + neighbor_mincost1[v][d];
  }

  changed = recompute_mincost1();

  if (TRACE > 0) {
    printf("\nrtupdate1(): received a packet from %d\n", v);
    printdt1(&dt1);
  }

  if (changed)
    sendmincost1();
}


printdt1(dtptr)
  struct distance_table *dtptr;
{
  printf("                via     \n");
  printf("   D1 |    0     2    3 \n");
  printf("  ----|-----------------\n");
  printf("dest 0|  %3d   %3d   %3d\n",
         dtptr->costs[0][0], dtptr->costs[0][2], dtptr->costs[0][3]);
  printf("     2|  %3d   %3d   %3d\n",
         dtptr->costs[2][0], dtptr->costs[2][2], dtptr->costs[2][3]);
  printf("     3|  %3d   %3d   %3d\n",
         dtptr->costs[3][0], dtptr->costs[3][2], dtptr->costs[3][3]);
}


linkhandler1(linkid, newcost)
  int linkid, newcost;
{
  int d;
  int changed;

  /* update direct link cost */
  connectcosts1[linkid] = newcost;

  /* update the direct-entry (dest=linkid via=linkid) */
  dt1.costs[linkid][linkid] = newcost;

  /* recompute all routes that go via this neighbor */
  for (d=0; d<4; d++) {
    if (newcost >= INFINITY || neighbor_mincost1[linkid][d] >= INFINITY)
      dt1.costs[d][linkid] = INFINITY;
    else
      dt1.costs[d][linkid] = newcost + neighbor_mincost1[linkid][d];
  }

  changed = recompute_mincost1();

  if (TRACE > 0) {
    printf("\nlinkhandler1(): link cost to %d changed to %d\n", linkid, newcost);
    printdt1(&dt1);
  }

  if (changed)
    sendmincost1();
}


/* ---------------- internal helper routines ---------------- */

static void sendmincost1()
{
  struct rtpkt pkt;
  int n;

  /* node 1 neighbors in classic topology: 0 and 2 */
  n = 0;
  if (connectcosts1[n] < INFINITY) {
    creatertpkt(&pkt, 1, n, mincost1);
    tolayer2(pkt);
  }

  n = 2;
  if (connectcosts1[n] < INFINITY) {
    creatertpkt(&pkt, 1, n, mincost1);
    tolayer2(pkt);
  }
}


static int recompute_mincost1()
{
  int d, v;
  int old, best;
  int changed;

  changed = 0;

  for (d=0; d<4; d++) {
    old = mincost1[d];
    best = INFINITY;

    for (v=0; v<4; v++) {
      if (dt1.costs[d][v] < best)
        best = dt1.costs[d][v];
    }

    mincost1[d] = best;
    if (old != best)
      changed = 1;
  }

  return changed;
}
