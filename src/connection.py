import socket
import queue
import time
import threading

import packet
import file

ALPHA = 1/8
BETA = 1/4
K = 4

class Connection():
    def __init__(self, dest_addr, q):
        self.dest_addr = dest_addr
        self.in_queue = queue.Queue()
        self.out_queue = q
        self.initialized = False
        self.first = False

        # foreign file_id -> native file_id
        self.file_id_table = {0 : 0}

        self.packets_for_future_files = {}

        self.first_timestamp = None
        self.rtt = 2
        self.rtt_var = self.rtt / 2
        self.rto = 1

        self.file_id = 1
        self.files = { 0 : file.File(self, 0, None, None) }

        self.window_cond = threading.Condition()
        self.max_window_size = 10
        self.curr_window_size = 0

    def __repr__(self):
        return "(init: {}, first: {})".format(self.initialized, self.first)

    def recv(self, p):
        self.in_queue.put(p)

    def start(self):
        threading.Thread(target=self.receive).start()
        threading.Thread(target=self.send).start()

    def receive(self):
        while True:
            p = self.in_queue.get()

            if p.type == packet.GET:
                if p.data == "":
                    print("no file")
                elif p.file_id not in self.file_id_table:
                    id = self.create_file(file.GET, p.data)
                    self.file_id_table[p.file_id] = id
                    link_packet = packet.Packet(packet_type=packet.CONTROL,
                                                flags=(False, False, True, False, False),
                                                file_id=id, data="link_file_id:{}".format(p.file_id))
                    self.send_packet(link_packet)
            elif p.type == packet.PUT:
                if p.data == "":
                    print("no file")
                elif p.file_id not in self.file_id_table:
                    id = self.create_file(file.PUT, p.data)
                    self.file_id_table[p.file_id] = id
                    link_packet = packet.Packet(packet_type=packet.CONTROL,
                                                flags=(False, False, True, False, False),
                                                file_id=id, data="link_file_id:{}".format(p.file_id))
                    self.send_packet(link_packet)

            if p.type == packet.CONTROL:
                options = p.data.split("\n")
                for o in options:
                    self.process_option(p, o)

            if p.file_id in self.file_id_table:
                p.file_id = self.file_id_table[p.file_id]
                if p.file_id in self.packets_for_future_files:
                    for p2 in self.packets_for_future_files[p.file_id][:]:
                        self.process_packet(p2)
                    self.packets_for_future_files.pop(p.file_id)
                self.process_packet(p)
            elif p.file_id in self.packets_for_future_files:
                self.packets_for_future_files[p.file_id].append(p)
            else:
                self.packets_for_future_files[p.file_id] = [p]

            print("file_id {} seq_num {} type {}".format(p.file_id, p.seq_num, p.type))

    def process_packet(self, p):
        if p.seq_num != 0:
            processed = self.files[p.file_id].ack_send(p.seq_num)
            if processed:
                return

        print("got here")

        if p.type == packet.DATA:
            self.files[p.file_id].write_chunk(p.seq_num, p.data)

        if (p.flags[packet.ACK]):
            rtt, count = self.files[p.file_id].ack_recv(p.ack_num)
            #self.window_cond.acquire()
            #while self.curr_window_size - count <= 0:
            #    self.window_cond.wait()
            #self.window_cond.release()
            #self.dec_curr_window_size(count)
            if rtt < float('inf'):
                self.rtt = (1-ALPHA)*self.rtt + ALPHA*rtt
                self.rtt_var = (1 - BETA) * self.rtt_var + BETA * abs(self.rtt - rtt)
                self.rto = max(1, self.rtt + K * self.rtt_var)
            print("rtt: {}; rto: {}".format(self.rtt, self.rto))
        if (p.flags[packet.SYN]):
            self.init()
            if (self.first == False):
                p2 = packet.Packet(flags=(True, False, True, False, False)) # SYN & ACK
            else:
                p2 = packet.Packet(flags=(False, False, True, False, False)) # ACK
            self.send_packet(p2)

    def process_option(self, p, o):
        args = o.split(":")
        if args[0] == "link_file_id":
            self.file_id_table[int(args[1])] = p.file_id
        native_id = self.file_id_table[p.file_id]
        if args[0] == "end_of_file":
            self.files[native_id].set_end_of_file(int(args[1]))

    def create_file(self, operation, path):
        id = self.file_id
        self.files[id] = file.File(self, id, operation, path)
        self.files[id].new_keep_alive_timer(self)
        self.file_id += 1
        return id

    def send(self):
        while True:
            for id in self.files.copy():
                f = self.files[id]
                if f.closed == True:
                    if f.finished(): 
                        pass#self.files.pop(id)
                elif f.operation == file.GET or f.operation == file.PUT_REQUEST:
                    d = f.get_next_chunk()
                    p = packet.Packet(packet_type=packet.DATA, file_id=f.file_id, data=d)
                    if len(d) == 0:
                        f.close()
                    while len(f.packets_sending) >= self.max_window_size:
                        pass
                    self.send_packet(p)

    def send_packet(self, p, pure_ack=False):
       # self.window_cond.acquire()
       # print("\n count=%d\n",self.curr_window_size)
       # while self.curr_window_size >= self.max_window_size:
       #     self.window_cond.wait()
       # self.window_cond.release()
        print(self.files)
        if p.seq_num == 0 and not pure_ack:
            p.seq_num = self.files[p.file_id].get_next_seq_num()
         #   self.inc_curr_window_size()
        if p.flags[packet.ACK]:
            p.ack_num = self.files[p.file_id].get_ack_num()
            self.files[p.file_id].cancel_keep_alive_timer()
            self.files[p.file_id].new_keep_alive_timer(self)
        self.out_queue.put((self.dest_addr, p))
        if not pure_ack:
            t = threading.Timer(self.rto, self.send_packet, (p,))
            t.start()
        else:
            t = None
        self.files[p.file_id].packets_sending.append((p, t, time.time()))

    def get_dest(self):
        return self.dest_addr

    def get_file(self, read_path, write_path):
        id = self.create_file(file.GET_REQUEST, write_path)
        p = packet.Packet(packet.GET, (False,)*5, file_id=id, data=read_path)
        self.send_packet(p)

    def put_file(self, read_path, write_path):
        id = self.create_file(file.PUT_REQUEST, read_path)
        p = packet.Packet(packet.PUT, (False,)*5, file_id=id, data=write_path)
        self.send_packet(p)

    def init(self):
        self.first_timestamp = time.time()
        self.files[0].new_keep_alive_timer(self)
        self.initialized = True

    def begin(self):
        self.first = True
        p = packet.Packet(flags=(True, False, False, False, False))
        self.send_packet(p)

    def inc_curr_window_size(self):
        self.window_cond.acquire()
        self.curr_window_size += 1
        self.window_cond.release()

    def dec_curr_window_size(self, count=1):
        self.window_cond.acquire()
        self.curr_window_size -= count
        self.window_cond.notify()
        self.window_cond.release()
