import socket
import queue
import time
import threading

import packet
import file

class Connection():
    def __init__(self, dest_addr, q):
        self.dest_addr = dest_addr
        self.in_queue = queue.Queue()
        self.out_queue = q
        self.initialized = False
        self.first = False
        self.acknowledged = 0
        self.timeout = None
        self.file_id = 1
        self.files = {}

    def __repr__(self):
        return "(init: {}, first: {})".format(self.initialized, self.first)

    def recv(self, p):
        self.in_queue.put(p)

    def start(self):
        threading.Thread(target=self.receive).start()
        threading.Thread(target=self.send).start()

    def receive(self):
        while True:
            p = self.in_queue.get()
            if (p.flags[packet.ACK]):
                self.acknowledged = p.ack_num
                self.update_timeout()
            if (p.flags[packet.SYN]):
                self.init(p)
                if (self.first == False):
                    p2 = packet.Packet(0, (True, False, True, False))
                else:
                    p2 = packet.Packet(0, (False, False, True, False))
                self.out_queue.put((self.dest_addr, p2))
            elif p.type == packet.GET:
                if p.data == "":
                    print("no file")
                else:
                    self.create_file(packet.GET, p.data)

    def update_timeout(self):
        if self.timeout:
            self.timeout.cancel()
        self.timeout = threading.Timer(5.0, print, ("timeout",))
        self.timeout.start()

    def create_file(self, operation, path):
        new_file_id = self.file_id
        self.file_id += 1
        self.files[new_file_id] = file.File(new_file_id, operation, path)

    def send(self):
        while True:
            for id in self.files.copy():
                f = self.files[id]
                if f.operation == packet.GET:
                    sent = f.send_next(self.dest_addr, self.out_queue)
                    if sent == 0: # envio completo 
                        self.files.pop(id)

    def get_dest(self):
        return self.dest_addr

    def get_file(self, path):
        p = packet.Packet(packet.GET, (False,)*4, data=path)
        self.out_queue.put((self.dest_addr, p))

    def init(self, p):
        self.initialized = True

    def begin(self):
        self.first = True
        p = packet.Packet(0, (True, False, False, False))
        self.out_queue.put((self.dest_addr, p))
