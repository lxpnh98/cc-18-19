import sys

from controller import Controller

conf = {
    "src_ip":"127.0.0.1",
    "src_port":"9999",
    "dst_ip":"127.0.0.1",
    "dst_port":"9999"
}

cc = Controller((conf["dst_ip"],int(conf["dst_port"])), (conf["dst_ip"],int(conf["dst_port"])))

if len(sys.argv) > 1:
    cc.start_connection()
