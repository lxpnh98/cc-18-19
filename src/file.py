import packet

class File:
    def __init__(self, operation, path):
        if operation == packet.GET:
            mode = "rb"
        elif operation == packet.PUT:
            mode = "wb"
        else:
            raise Exception("unknown operation {}".format(operation))
        self.file = open(path, mode)

