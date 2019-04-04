# Type constants
GET=0
PUT=1
DATA=2
CONTROL=3

class Packet:
    def __init__(self, src_port, src_ip, packet_type, flags):
        self.src_port = src_port
        self.src_ip = src_ip
        self.type = packet_type
        self.flags  = flags # (syn, fin, ack, nack)

    def __repr__(self):
        return ("Packet({}, {}, {}, {})"
            .format(self.src_port, self.src_ip, self.type, self.flags))


    def encode(self):
        return chr(((self.type & 0x3) << 6) | # XX00 0000
                    (self.flags[0] << 5 |     # 00X0 0000
                     self.flags[1] << 4 |     # 000X 0000
                     self.flags[2] << 3 |     # 0000 X000
                     self.flags[3] << 2))     # 0000 0X00

def extract(char, rshift, mask):
    return (char >> rshift) & mask

def decode(data, addr):
    packet_type = extract(data[0], 6, 0x3) # XX00 0000
    flags =       extract(data[0], 2, 0xf)
    syn = flags  & 0x8                     # 00X0 0000
    fin = flags  & 0x4                     # 000X 0000
    ack = flags  & 0x2                     # 0000 X000
    nack = flags & 0x1                     # 0000 0X00
    return Packet(addr[0], addr[1], packet_type,
                  (bool(syn), bool(fin), bool(ack), bool(nack)))

