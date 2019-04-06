import threading
import socket

from connection import Connection
import packet

class Receiver(threading.Thread):
    def __init__(self, addr, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.connections = {}
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(addr)
        
    def run(self):
        while True:
            data, addr = self.socket.recvfrom(1024)
            if not addr in self.connections:
                self.connections[addr] = Connection(self.socket, addr, self.queue)
            p = packet.decode(data, addr)
            self.connections[addr].recv(p)

