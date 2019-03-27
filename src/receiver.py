import threading
import socket

from connection import Connection

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
                print("New connection created")
            else:
                print("Connection already exists.")
            connections[addr].recv(data)

if __name__=='__main__':
    r = Receiver()
    r.start()
