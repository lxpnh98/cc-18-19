import socket
import queue
import time
import threading

import packet

class Connection(threading.Thread):
    def __init__(self, dest_addr, q):
        threading.Thread.__init__(self)
        self.dest_addr = dest_addr
        self.in_queue = queue.Queue()
        self.out_queue = q
        self.initialized = False
        self.first = False

    def __repr__(self):
        return "(init: {}, first: {})".format(self.initialized, self.first)

    def recv(self, p):
        self.in_queue.put(p)

    def run(self):
        while True:
            p = self.in_queue.get()
            if (p.flags[packet.SYN]):
                self.init(p)
                if (self.first == False):
                    p2 = packet.Packet(0, (True, False, True, False))
                else:
                    p2 = packet.Packet(0, (False, False, True, False))
                self.out_queue.put((self.dest_addr, p2))

    def get_dest(self):
        return self.dest_addr

    def init(self, p):
        self.initialized = True

    def begin(self):
        self.first = True
        p = packet.Packet(0, (True, False, False, False))
        self.out_queue.put((self.dest_addr, p))
