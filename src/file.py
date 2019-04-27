import packet

class File:
    def __init__(self, file_id, operation, path):
        self.file_id = file_id
        self.operation = operation

        if operation == packet.GET:
            mode = "r"
        elif operation == packet.PUT:
            mode = "w"
        else:
            raise Exception("unknown operation {}".format(operation))
        self.file = open(path, mode)

    def send_next(self, dest_addr, queue):
        d = self.file.read(1000)
        p = packet.Packet(packet.DATA, file_id=self.file_id, data=d)
        queue.put((dest_addr, p))
        return len(d)
