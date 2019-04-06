import socket

class Connection():
    def __init__(self, socket, dest_addr, queue):
        self.dest_addr = dest_addr
        self.socket = socket
        self.queue = queue

    def recv(self, packet):
        print("Received msg from {}: {}".format(self.socket.getsockname(), packet))
        # send packet back for testing
        self.queue.put((self, packet))

    def get_dest(self):
        return self.dest_addr

