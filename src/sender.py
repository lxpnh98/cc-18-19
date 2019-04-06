import threading
import socket

import packet

class Sender(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        '''
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(MESSAGE, (UDP_IP, UDP_PORT))
        '''
        while True:
            conn, packet = self.queue.get()
            conn.socket.sendto(bytearray(packet.encode(), 'iso-8859-15'), conn.get_dest())
            print("Sent packet {} to {}".format(packet, conn.get_dest()))

