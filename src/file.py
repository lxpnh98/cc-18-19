import packet

class File:
    def __init__(self, operation, path):
        self.operation = operation

        if operation == packet.GET:
            mode = "rb"
        elif operation == packet.PUT:
            mode = "wb"
        else:
            raise Exception("unknown operation {}".format(operation))
        self.file = open(path, mode)

    def send_next(self, dest_addr, queue):
        s = self.file.read(1000)
        queue.put((dest_addr, s))
