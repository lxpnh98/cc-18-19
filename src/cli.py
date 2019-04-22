import sys

from controller import Controller

conf = {
    "src_ip":"127.0.0.1",
    "src_port":"9999",
    "dst_ip":"127.0.0.1",
    "dst_port":"9999"
}

cc = None

while True:
    print("> ", end="")
    query = input()
    terms = query.split(" ")
    try:
        if terms[0] == "start":
            cc = Controller((conf["src_ip"],int(conf["src_port"])), (conf["dst_ip"],int(conf["dst_port"])))
        if terms[0] == "connect":
            if cc:
                cc.start_connection()
        elif terms[0] == "set":
            if terms[1] in conf:
                conf[terms[1]] = terms[2]
        print(conf["dst_port"])
        print(conf["src_port"])
    except IndexError:
        print("wrong number of arguments")
