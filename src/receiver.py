import threading
import socket

from connection import Connection
import packet

class Receiver(threading.Thread):
    def __init__(self, sock, queue, connections):
        threading.Thread.__init__(self)
        self.queue = queue
        self.connections = connections
        self.socket = sock
        
    def run(self):
        while True:
            data, addr = self.socket.recvfrom(1024)
            if not addr in self.connections:
                self.connections[addr] = Connection(addr, self.queue)
            p = packet.decode(data)
            print("Received msg from {}: {}".format(self.socket.getsockname(), p))
            self.connections[addr].recv(p)

