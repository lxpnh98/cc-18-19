import sys
import socket
from queue import Queue

from receiver import Receiver
from sender import Sender
from packet import Packet
from connection import Connection


SRC_ADDR = ("127.0.0.1", int(sys.argv[1]))
DST_ADDR = ("127.0.0.1", int(sys.argv[2]))

q = Queue()
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(SRC_ADDR)
connections = {}

r = Receiver(sock, q, connections)
s = Sender(sock, q)
r.start()
s.start()

# initial packet to be sent back and forth
if len(sys.argv) == 4:
    c = Connection(DST_ADDR, q)
    connections[DST_ADDR] = c
    c.begin()

