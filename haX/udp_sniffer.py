import socket
import os

# host to listen on
host = "192.168.8.152"

# check for OS and bind socket to public interface
if os.name == "nt":
    socket_protocol = socket.IPPROTO_IP
else:
    socket_protocol = socket.IPPROTO_ICMP

# create raw socket
sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)

sniffer.bind((host, 0))

# set the option to include headers
sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
