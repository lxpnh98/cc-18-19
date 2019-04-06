import socket
from queue import Queue

from receiver import Receiver
from sender import Sender
from packet import Packet
from connection import Connection

UDP_IP = "127.0.0.1"
UDP_PORT = 9999

q = Queue()
r = Receiver((UDP_IP, UDP_PORT), q)
s = Sender(q)
r.start()
s.start()

# initial packet to be sent back and forth
p = Packet("127.0.0.1", 5000, 0, (False, False, False, False))
c = Connection(r.socket, ("127.0.0.1", 9999), q)
q.put((c, p))

