import sys

from controller import Controller

conf = {
    "src_ip":"127.0.0.1",
    "src_port":"9999",
    "dst_ip":"127.0.0.1",
    "dst_port":"9999"
}

cc = None
conn = None

while True:
    print("> ", end="")
    query = input()
    terms = query.split(" ")
    try:
        if terms[0] == "start":
            cc = Controller((conf["src_ip"],int(conf["src_port"])), (conf["dst_ip"],int(conf["dst_port"])))
        if terms[0] == "connect":
            if cc:
                conn = cc.get_connection((conf["dst_ip"],int(conf["dst_port"])))
                if not conn:
                    conn = cc.start_connection()
            else:
                print("need to 'start' first")
        elif terms[0] == "set":
            if terms[1] in conf:
                conf[terms[1]] = terms[2]
            else:
                print("{} not a valid setting".format(terms[1]))
        elif terms[0] == "get":
            if conn:
                conn.get_file(terms[1], terms[2])
        elif terms[0] == "put":
            if conn:
                conn.put_file(terms[1], terms[2])
        elif terms[0] == "fin":
            if conn:
                conn.fin_connection()
                print("\n\nfin started\n\n")

    except IndexError:
        print("too few arguments")
