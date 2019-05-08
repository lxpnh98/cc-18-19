import threading
import time
import os

import packet

GET=0
PUT=1
GET_REQUEST=2
PUT_REQUEST=3

class File:
    def __init__(self, conn, file_id, operation, path):
        self.file_id = file_id
        self.operation = operation
        self.seq_num = 1
        self.ack_num = 0
        self.packets_sending = []
        self.acks_to_send = []
        self.keep_alive_timer = None
        self.new_keep_alive_timer(conn)

        self.eof = None
        self.chunks_to_write = []
        self.chunk_num = 1
        self.closed = False

        if file_id != 0:
            if operation == GET or operation == PUT_REQUEST:
                mode = "r"
            elif operation == PUT or operation == GET_REQUEST:
                mode = "w"
            else:
                raise Exception("unknown operation {}".format(operation))
            self.file = open(path, mode, encoding='iso-8859-15')
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

    def write_chunk(self, seq_num, chunk):
        if self.file and self.operation in [PUT, GET_REQUEST]:
            self.chunks_to_write.append((seq_num, chunk))
            for s, c in sorted(self.chunks_to_write, key=lambda x: x[0]):
                if c == "":
                    self.close()
                    self.set_end_of_file(s-1)
                    break
                print("chunk_seq_num: {}".format(s))
                if s == self.chunk_num + 1:
                    self.file.write(c)
                    self.chunk_num += 1
                    self.chunks_to_write.remove((s, c))
                elif s <= self.chunk_num:
                    self.chunks_to_write.remove((s, c))
                else:
                    break
            self.file.flush()
            os.fsync(self.file.fileno())

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
        current_timestamp = time.time()
        count = 0
        rtt = float('inf')
        for p, t, timestamp in self.packets_sending[:]:
            if p.seq_num <= ack_num:
                count += 1
                if t: t.cancel()
                rtt = min(rtt, current_timestamp - timestamp)
                self.packets_sending.remove((p, t, timestamp))
        return rtt, count

    def cancel_keep_alive_timer(self):
        if self.keep_alive_timer:
            self.keep_alive_timer.cancel()
        print("file_id {} chunk {} eof {}".format(self.file_id, self.chunk_num, self.eof))
        if self.eof and self.chunk_num == self.eof:
            self.close()

    def new_keep_alive_timer(self, conn):
        p = packet.Packet(flags=(False, False, True, False, False), file_id=self.file_id, data="test")
        self.keep_alive_timer = threading.Timer(conn.rto, conn.send_packet, (p,), {"pure_ack":True})
        self.keep_alive_timer.start()

    def set_end_of_file(self, seq_num):
        self.eof = seq_num

    def close(self):
        for p, t, timestamp in self.packets_sending[:]:
            if t:
                t.cancel()
        self.file.close()
        if self.keep_alive_timer:
            self.keep_alive_timer.cancel()
        self.closed = True

    def finished(self):
        return not self.packets_sending and not self.acks_to_send
