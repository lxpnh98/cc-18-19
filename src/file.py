import threading

import packet

GET=0
PUT=1
GET_REQUEST=2
PUT_REQUEST=3

class File:
    def __init__(self, file_id, operation, path):
        self.file_id = file_id
        self.operation = operation
        self.seq_num = 1
        self.ack_num = 0
        self.packets_sending = []
        self.acks_to_send = []
        self.keep_alive_timer = None

        if file_id != 0:
            if operation == GET or operation == PUT_REQUEST:
                mode = "r"
            elif operation == PUT or operation == GET_REQUEST:
                mode = "w"
            else:
                raise Exception("unknown operation {}".format(operation))
            self.file = open(path, mode)
        else:
            self.file = None

    def get_next_seq_num(self):
        s = self.seq_num
        self.seq_num += 1
        return s

    def get_ack_num(self):
        return self.ack_num

    def get_next_chunk(self):
        if self.file:
            return self.file.read(1000)
        else:
            raise Exception("file not opened")

    def ack_send(self, ack_num):
        if self.ack_num >= ack_num:
            return True # already processed
        self.acks_to_send.append(ack_num)
        for ack in sorted(self.acks_to_send):
            if self.ack_num + 1 == ack:
                self.ack_num = ack
                self.acks_to_send.remove(ack)
            elif self.ack_num >= ack:
                self.acks_to_send.remove(ack)
        return False

    def ack_recv(self, ack_num):
        for p, t in self.packets_sending[:]:
            if p.seq_num <= ack_num:
                t.cancel()
                self.packets_sending.remove((p, t))

    def update_keep_alive_timer(self, conn):
        if self.keep_alive_timer:
            self.keep_alive_timer.cancel()
        p = packet.Packet(flags=(False, False, True, False), file_id=self.file_id, data="test")
        self.keep_alive_timer = threading.Timer(5.0, conn.send_packet, (p,), {"pure_ack":True})
        self.keep_alive_timer.start()

