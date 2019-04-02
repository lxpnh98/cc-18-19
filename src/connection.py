import socket

class Connection():
    def __init__(self, addr):
        self.ip = addr[0]
        self.port = addr[1]
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def recv(self, msg):
        print("Received msg from ({},{}): {}".format(self.ip, self.port, msg.decode('iso-8859-15'))) 
        self.socket.sendto(b"Message received", (self.ip, self.port))

