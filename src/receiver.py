import threading
import socket

from connection import Connection
import packet

UDP_IP = "127.0.0.1"
UDP_PORT = 9999

connections = {}

class Receiver(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        
    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        s.bind((UDP_IP, UDP_PORT)) # listen on port UDP_PORT

        while True:
            data, addr = s.recvfrom(1024)
            if not addr in connections:
                connections[addr] = Connection(addr)
            p = packet.decode(data, addr)
            connections[addr].recv(p)


if __name__=='__main__':
    r = Receiver()
    r.start()
