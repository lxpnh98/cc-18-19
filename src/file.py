import packet

class File:
    def __init__(self, file_id, operation, path):
        self.file_id = file_id
        self.operation = operation
        self.seq_num = 1
        self.ack_num = 0
        self.packets_sending = []
        self.acks_to_send = []

        if file_id != 0:
            if operation == packet.GET:
                mode = "r"
            elif operation == packet.PUT:
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
        self.acks_to_send.append(ack_num)
        for ack in sorted(self.acks_to_send):
            if self.ack_num + 1 == ack:
                self.ack_num = ack
                self.acks_to_send.remove(ack)

    def ack_recv(self, ack_num):
        for p, t in self.packets_sending[:]:
            if p.seq_num <= ack_num:
                t.cancel()
                self.packets_sending.remove((p, t))

