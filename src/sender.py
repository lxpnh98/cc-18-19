import threading
import socket

import packet

UDP_IP = "127.0.0.1"
UDP_PORT = 9999
MESSAGE = bytearray(packet.Packet(123, 456, 2, (True, False, False, False)).encode(), 'iso-8859-15')

class Sender(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(MESSAGE, (UDP_IP, UDP_PORT))

        s.sendto(MESSAGE, (UDP_IP, UDP_PORT))

        #receive
        data, addr = s.recvfrom(1024)
        print("Received msg from ({},{}): {}".format(addr[0], addr[0], data.decode())) 

if __name__=='__main__':
    s = Sender()
    s.start()
