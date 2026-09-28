from socket import *
import os
import sys
import struct
import time
import select

ICMP_ECHO_REQUEST = 8

def checksum(string):
    csum = 0
    countTo = (len(string) // 2) * 2
    count = 0

    while count < countTo:
        thisVal = string[count + 1] * 256 + string[count]
        csum = csum + thisVal
        csum = csum & 0xffffffff
        count += 2

    if countTo < len(string):
        csum += string[len(string) - 1]
        csum = csum & 0xffffffff

    csum = (csum >> 16) + (csum & 0xffff)
    csum += (csum >> 16)
    answer = ~csum & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer


def receiveOnePing(mySocket, ID, timeout, destAddr):
    timeLeft = timeout

    while True:
        startedSelect = time.time()
        ready = select.select([mySocket], [], [], timeLeft)
        howLongInSelect = time.time() - startedSelect

        if ready[0] == []:
            return "Request timed out."

        timeReceived = time.time()
        recPacket, addr = mySocket.recvfrom(1024)

        # ICMP header starts after IP header (20 bytes)
        icmpHeader = recPacket[20:28]
        icmpType, code, checksum_rcv, packetID, sequence = struct.unpack(
            "bbHHh", icmpHeader
        )

        if icmpType == 0 and packetID == ID:
            bytes = struct.calcsize("d")
            timeSent = struct.unpack(
                "d", recPacket[28:28 + bytes]
            )[0]
            return f"Reply from {addr[0]}: time={(timeReceived - timeSent) * 1000:.2f} ms"

        timeLeft -= howLongInSelect
        if timeLeft <= 0:
            return "Request timed out."


def sendOnePing(mySocket, destAddr, ID):
    myChecksum = 0
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    data = struct.pack("d", time.time())

    myChecksum = checksum(header + data)
    myChecksum = htons(myChecksum)

    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    packet = header + data

    mySocket.sendto(packet, (destAddr, 1))


def doOnePing(destAddr, timeout):
    icmp = getprotobyname("icmp")
    mySocket = socket(AF_INET, SOCK_RAW, icmp)
    myID = os.getpid() & 0xFFFF

    sendOnePing(mySocket, destAddr, myID)
    delay = receiveOnePing(mySocket, myID, timeout, destAddr)

    mySocket.close()
    return delay


def ping(host, timeout=1):
    dest = gethostbyname(host)
    print(f"Pinging {host}:{dest} using Python:\n")

    while True:
        print(doOnePing(dest, timeout))
        time.sleep(1)

ping("www.google.com")