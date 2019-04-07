import threading
import socket

import packet

class Sender(threading.Thread):
    def __init__(self, sock, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.socket = sock

    def run(self):
        while True:
            addr, packet = self.queue.get()
            self.socket.sendto(bytearray(packet.encode(), 'iso-8859-15'), addr)
            print("Sent packet {} to {}".format(packet, addr))

