import sys
import socket
from queue import Queue

from receiver import Receiver
from sender import Sender
from packet import Packet
from connection import Connection

class Controller:
    def __init__(self, source_addr, dest_addr):
        self.source_addr = source_addr
        self.dest_addr = dest_addr
        self.q = Queue()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(source_addr)
        self.connections = {}

        self.r = Receiver(self.sock, self.q, self.connections)
        self.s = Sender(self.sock, self.q)
        self.r.start()
        self.s.start()

    def start_connection(self):
        c = Connection(self.dest_addr, self.q)
        self.connections[self.dest_addr] = c
        c.begin()

if __name__=='__main__':
    SRC_ADDR = ("127.0.0.1", int(sys.argv[1]))
    DST_ADDR = ("127.0.0.1", int(sys.argv[2]))
    cc = Controller(SRC_ADDR, DST_ADDR)
    if len(sys.argv) == 4:
        cc.start_connection()
