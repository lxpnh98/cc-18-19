import socket
import queue
import time
import threading

import packet
import file

class Connection():
    def __init__(self, dest_addr, q):
        self.dest_addr = dest_addr
        self.in_queue = queue.Queue()
        self.out_queue = q
        self.initialized = False
        self.first = False

        self.file_id = 1
        self.files = { 0 : file.File(0, None, None) }

        # foreign file_id -> native file_id
        self.file_id_table = {0 : 0}


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
                                                flags=(False, False, True, False),
                                                file_id=id, data="link_file_id:{}".format(p.file_id))
                    self.send_packet(link_packet)
            elif p.type == packet.PUT:
                if p.data == "":
                    print("no file")
                elif p.file_id not in self.file_id_table:
                    id = self.create_file(file.PUT, p.data)
                    self.file_id_table[p.file_id] = id
                    link_packet = packet.Packet(packet_type=packet.CONTROL,
                                                flags=(False, False, True, False),
                                                file_id=id, data="link_file_id:{}".format(p.file_id))
                    self.send_packet(link_packet)

            if p.type == packet.CONTROL:
                options = p.data.split("\n")
                for o in options:
                    self.process_option(p, o)

            p.file_id = self.file_id_table[p.file_id]

            if p.seq_num != 0:
                processed = self.files[p.file_id].ack_send(p.seq_num)
                if processed:
                    continue

            if p.type == packet.DATA:
                self.files[p.file_id].write_chunk(p.seq_num, p.data)

            if (p.flags[packet.ACK]):
                self.files[p.file_id].ack_recv(p.ack_num)
            if (p.flags[packet.SYN]):
                self.init(p)
                if (self.first == False):
                    p2 = packet.Packet(flags=(True, False, True, False))
                else:
                    p2 = packet.Packet(flags=(False, False, True, False))
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
        self.files[id] = file.File(id, operation, path)
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
                    if len(d) != 0:
                        p = packet.Packet(packet_type=packet.DATA, file_id=f.file_id, data=d)
                    else:
                        p = packet.Packet(packet_type=packet.CONTROL, file_id=f.file_id, data="end_of_file:{}".format(f.seq_num-1))
                        f.close()
                    self.send_packet(p)
                        

    def send_packet(self, p, pure_ack=False):
        if p.seq_num == 0 and not pure_ack:
            p.seq_num = self.files[p.file_id].get_next_seq_num()
        if p.flags[packet.ACK]:
            p.ack_num = self.files[p.file_id].get_ack_num()
        self.out_queue.put((self.dest_addr, p))
        t = threading.Timer(5.0, self.send_packet, (p,))
        self.files[p.file_id].packets_sending.append((p, t))
        if not self.files[p.file_id].update_keep_alive_timer(self) and self.files[p.file_id].finished():
            pass#self.files.pop(p.file_id)
        t.start()

    def get_dest(self):
        return self.dest_addr

    def get_file(self, read_path, write_path):
        id = self.create_file(file.GET_REQUEST, write_path)
        p = packet.Packet(packet.GET, (False,)*4, file_id=id, data=read_path)
        self.send_packet(p)

    def put_file(self, read_path, write_path):
        id = self.create_file(file.PUT_REQUEST, read_path)
        p = packet.Packet(packet.PUT, (False,)*4, file_id=id, data=write_path)
        self.send_packet(p)

    def init(self, p):
        self.initialized = True

    def begin(self):
        self.first = True
        p = packet.Packet(flags=(True, False, False, False))
        self.send_packet(p)

