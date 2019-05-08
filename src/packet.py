import random

# Type constants
GET=0
PUT=1
DATA=2
CONTROL=3

# Flags
SYN=0
FIN=1
ACK=2
NACK=3
ERROR=4

class Packet:
    def __init__(self, packet_type=CONTROL, flags=(False,False,True,False,False), file_id=0, seq_num=0, ack_num=0, data=""):
        self.type = packet_type
        self.flags = flags # (syn, fin, ack, nack)
        self.file_id = file_id
        self.seq_num = seq_num
        self.ack_num = ack_num
        self.data = data

    def get_checksum(self, header=None, payload=None):
        if header:
            h = header
        else:
            h = (bytes((chr(((self.type & 0x3) << 6) | # XX00 0000
                        (self.flags[0] << 5 |          # 00X0 0000
                         self.flags[1] << 4 |          # 000X 0000
                         self.flags[2] << 3 |          # 0000 X000
                         self.flags[3] << 2 |          # 0000 0X00
                         self.flags[4] << 1))          # 0000 00X0
                    + chr(self.file_id & 0xff)), 'iso-8859-15')
                    + self.seq_num.to_bytes(4, byteorder='big')
                    + self.ack_num.to_bytes(4, byteorder='big'))
        if payload:
            d = payload
        else:
            d = bytes(self.data, 'iso-8859-15')

        checksum = 0
        i = 1
        for c in h + d:
            checksum += c*i
            checksum %= 2**16 # must fit in 2 bytes
            i += 1
        return checksum

    def __repr__(self):
        return ("Packet({}, {}, {}, {}, {}, \"{}\")"
            .format(self.type, self.flags, self.file_id, self.seq_num, self.ack_num, self.data if len(self.data) < 20 else "(...)" ))

    def encode(self):
        h = (bytes((chr(((self.type & 0x3) << 6) | # XX00 0000
                    (self.flags[0] << 5 |          # 00X0 0000
                     self.flags[1] << 4 |          # 000X 0000
                     self.flags[2] << 3 |          # 0000 X000
                     self.flags[3] << 2 |          # 0000 0X00
                     self.flags[4] << 1))          # 0000 00X0
                + chr(self.file_id & 0xff)), 'iso-8859-15')
                + self.seq_num.to_bytes(4, byteorder='big')
                + self.ack_num.to_bytes(4, byteorder='big'))
        d = bytes(self.data, 'iso-8859-15')
        checksum = self.get_checksum(h, d).to_bytes(2, byteorder='big')
        return h + checksum + d

    def is_valid_checksum(self, checksum):
        return self.get_checksum() == int.from_bytes(checksum, byteorder='big')

def extract(char, rshift, mask):
    return (char >> rshift) & mask

def decode(data):
    packet_type = extract(data[0], 6, 0x3)    # XX00 0000
    flags =       extract(data[0], 1, 0x1f)
    syn = flags  & 0x10                       # 00X0 0000
    fin = flags  & 0x8                        # 000X 0000
    ack = flags  & 0x4                        # 0000 X000
    nack = flags & 0x2                        # 0000 0X00
    error = flags & 0x1                       # 0000 00X0
    file_id = data[1]
    seq_num = data[2:6]
    ack_num = data[6:10]
    checksum = data[10:12]
    payload = data[12:].decode('iso-8859-15')
    packet = Packet(packet_type,
                  (bool(syn), bool(fin), bool(ack), bool(nack), bool(error)),
                  file_id, int.from_bytes(seq_num, byteorder='big'), int.from_bytes(ack_num, byteorder='big'),
                  payload)
    #if packet.is_valid_checksum(checksum) and random.random() >= 0.1: # para testar
    if packet.is_valid_checksum(checksum):
        return packet
    else:
        return None
