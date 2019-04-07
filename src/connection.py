import socket
import time

import packet

class Connection():
    def __init__(self, dest_addr, queue):
        self.dest_addr = dest_addr
        self.queue = queue
        self.initialized = False
        self.first = False

    def __repr__(self):
        return "(init: {}, first: {})".format(self.initialized, self.first)

    def recv(self, p):
        if (p.flags[packet.SYN]):
            self.init(p)
            if (self.first == False):
                p2 = packet.Packet(0, (True, False, True, False))
            else:
                p2 = packet.Packet(0, (False, False, True, False))
            self.queue.put((self.dest_addr, p2))

    def get_dest(self):
        return self.dest_addr

    def init(self, p):
        self.initialized = True

    def begin(self):
        self.first = True
        p = packet.Packet(0, (True, False, False, False))
        self.queue.put((self.dest_addr, p))
