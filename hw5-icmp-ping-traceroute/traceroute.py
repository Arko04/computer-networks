from socket import *
import os
import struct
import time
import select

ICMP_ECHO_REQUEST = 8
MAX_HOPS = 30
TIMEOUT = 2.0
TRIES = 2


def checksum(string):
    csum = 0
    countTo = (len(string) // 2) * 2
    count = 0

    while count < countTo:
        thisVal = string[count + 1] * 256 + string[count]
        csum += thisVal
        csum &= 0xffffffff
        count += 2

    if countTo < len(string):
        csum += string[len(string) - 1]
        csum &= 0xffffffff

    csum = (csum >> 16) + (csum & 0xffff)
    csum += (csum >> 16)
    answer = ~csum & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer


def build_packet():
    myID = os.getpid() & 0xFFFF
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, 0, myID, 1)
    data = struct.pack("d", time.time())
    myChecksum = checksum(header + data)
    myChecksum = htons(myChecksum)
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, myID, 1)
    return header + data


def get_route(hostname):
    destAddr = gethostbyname(hostname)
    print(f"Traceroute to {hostname} ({destAddr})\n")

    for ttl in range(1, MAX_HOPS + 1):
        for _ in range(TRIES):
            mySocket = socket(AF_INET, SOCK_RAW, getprotobyname("icmp"))
            mySocket.setsockopt(IPPROTO_IP, IP_TTL, struct.pack('I', ttl))
            mySocket.settimeout(TIMEOUT)

            try:
                packet = build_packet()
                mySocket.sendto(packet, (hostname, 0))
                t = time.time()

                ready = select.select([mySocket], [], [], TIMEOUT)
                if ready[0] == []:
                    print(f"{ttl} * * * Request timed out.")
                    continue

                recvPacket, addr = mySocket.recvfrom(1024)
                timeReceived = time.time()

                icmpHeader = recvPacket[20:28]
                types, code, checksum_rcv, packetID, sequence = struct.unpack(
                    "bbHHh", icmpHeader
                )

                rtt = (timeReceived - t) * 1000

                if types == 11:
                    print(f"{ttl} {addr[0]} rtt={rtt:.2f} ms")
                elif types == 3:
                    print(f"{ttl} {addr[0]} Destination unreachable")
                elif types == 0:
                    print(f"{ttl} {addr[0]} rtt={rtt:.2f} ms")
                    return
                else:
                    print(f"{ttl} Unknown ICMP type")

            except timeout:
                print(f"{ttl} * * * Request timed out.")
            finally:
                mySocket.close()


if __name__ == "__main__":
    get_route("google.com")
