#include <stdio.h>

#define INFINITY 999

struct rtpkt {
  int sourceid;       /* id of sending router sending this pkt */
  int destid;         /* id of router to which pkt being sent
                         (must be an immediate neighbor) */
  int mincost[4];     /* min cost to node 0 ... 3 */
};

extern int TRACE;
extern int YES;
extern int NO;

extern void tolayer2();
extern void creatertpkt();

/* direct link costs from node 0 to others */
int connectcosts0[4] = { 0, 1, 3, 7 };

/* last distance vectors received from each neighbor (used for link changes) */
int neighbor_mincost0[4][4];

/* node 0 current minimum costs */
int mincost0[4];

struct distance_table
{
  int costs[4][4];
} dt0;

/* internal helpers (K&R style) */
static void sendmincost0();
static int recompute_mincost0();

/* students to write the following routines */

void rtinit0()
{
  int i, j;

  /* initialize distance table and saved neighbor vectors to INFINITY */
  for (i=0; i<4; i++) {
    for (j=0; j<4; j++) {
      dt0.costs[i][j] = INFINITY;
      neighbor_mincost0[i][j] = INFINITY;
    }
  }

  /* costs to self */
  dt0.costs[0][0] = 0;

  /* direct link costs (via the neighbor itself) */
  dt0.costs[1][1] = connectcosts0[1];
  dt0.costs[2][2] = connectcosts0[2];
  dt0.costs[3][3] = connectcosts0[3];

  /* initial mincost vector is just direct costs */
  for (i=0; i<4; i++)
    mincost0[i] = connectcosts0[i];

  if (TRACE > 0) {
    printf("\nrtinit0() called\n");
    printdt0(&dt0);
  }

  /* send initial distance vector to neighbors */
  sendmincost0();
}


void rtupdate0(rcvdpkt)
  struct rtpkt *rcvdpkt;
{
  int v, d;
  int changed;

  v = rcvdpkt->sourceid;

  /* record neighbor's latest vector */
  for (d=0; d<4; d++)
    neighbor_mincost0[v][d] = rcvdpkt->mincost[d];

  /* update our distance table column for 'via v' */
  for (d=0; d<4; d++) {
    if (connectcosts0[v] >= INFINITY || neighbor_mincost0[v][d] >= INFINITY)
      dt0.costs[d][v] = INFINITY;
    else
      dt0.costs[d][v] = connectcosts0[v] + neighbor_mincost0[v][d];
  }

  changed = recompute_mincost0();

  if (TRACE > 0) {
    printf("\nrtupdate0(): received a packet from %d\n", v);
    printdt0(&dt0);
  }

  if (changed)
    sendmincost0();
}


printdt0(dtptr)
  struct distance_table *dtptr;

{
  printf("                via     \n");
  printf("   D0 |    1     2    3 \n");
  printf("  ----|-----------------\n");
  printf("     1|  %3d   %3d   %3d\n",dtptr->costs[1][1],
         dtptr->costs[1][2],dtptr->costs[1][3]);
  printf("dest 2|  %3d   %3d   %3d\n",dtptr->costs[2][1],
         dtptr->costs[2][2],dtptr->costs[2][3]);
  printf("     3|  %3d   %3d   %3d\n",dtptr->costs[3][1],
         dtptr->costs[3][2],dtptr->costs[3][3]);
}

// NOTE: Bonus link-change handlers are required only for node0 and node1 per the PDF.

linkhandler0(linkid, newcost)
  int linkid, newcost;

/* called when cost from 0 to linkid changes from current value to newcost */

{
  int d;
  int changed;

  /* update direct link cost */
  connectcosts0[linkid] = newcost;

  /* update the direct-entry (dest=linkid via=linkid) */
  dt0.costs[linkid][linkid] = newcost;

  /* recompute all routes that go via this neighbor */
  for (d=0; d<4; d++) {
    if (newcost >= INFINITY || neighbor_mincost0[linkid][d] >= INFINITY)
      dt0.costs[d][linkid] = INFINITY;
    else
      dt0.costs[d][linkid] = newcost + neighbor_mincost0[linkid][d];
  }

  changed = recompute_mincost0();

  if (TRACE > 0) {
    printf("\nlinkhandler0(): link cost to %d changed to %d\n", linkid, newcost);
    printdt0(&dt0);
  }

  if (changed)
    sendmincost0();
}


/* ---------------- internal helper routines ---------------- */

static void sendmincost0()
{
  struct rtpkt pkt;
  int n;

  /* node 0 neighbors: 1,2,3 */
  for (n=1; n<=3; n++) {
    if (connectcosts0[n] < INFINITY) {
      creatertpkt(&pkt, 0, n, mincost0);
      tolayer2(pkt);
    }
  }
}


static int recompute_mincost0()
{
  int d, v;
  int old, best;
  int changed;

  changed = 0;

  for (d=0; d<4; d++) {
    old = mincost0[d];
    best = INFINITY;
    for (v=0; v<4; v++) {
      if (dt0.costs[d][v] < best)
        best = dt0.costs[d][v];
    }
    mincost0[d] = best;
    if (old != best)
      changed = 1;
  }

  return changed;
}
