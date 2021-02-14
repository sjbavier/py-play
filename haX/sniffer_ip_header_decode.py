import os
import socket
import struct 
from ctypes import *

# host to listen on
host = "192.168.8.173"

# our IP header
class IP(Structure):
    
    # using c structure to map buffer into IP header
    _fields_ = [
        ("ihl", c_ubyte, 4), 
        ("version", c_ubyte, 4),
        ("tos", c_ubyte),
        ("len", c_ushort),
        ("id", c_ushort),
        ("offset", c_short),
        ("ttl", c_ubyte),
        ("protocol_num", c_ubyte),
        ("sum", c_ushort),
        ("src", c_ulong),
        ("dst", c_ulong)
    ]
    
    def __new__(self, socket_buffer=None):
        
        # from ctypes datatypes from_buffer_copy creates a ctypes instance
        return self.from_buffer_copy(socket_buffer)
    
    def __init__(self, socket_buffer=None):
        
        # map protocol constants to their name
        self.protocol_map = {1:"ICMP", 6:"TCP", 17:"UDP"}
        
        print(struct.unpack('! L', self.src))
        
        # human readable IP addresses
        # inet_ntoa converts 32 bit packed IPv4 to dotted-quad string
        self.src_address = socket.inet_ntoa(struct.pack("<L", self.src))
        self.dst_address = socket.inet_ntoa(struct.pack("<L", self.dst))
        
        # human readable protocol
        try:
            self.protocol = self.protocol_map[self.protocol_num]
        except:
            self.protocol = str(self.protocol_num)
            
# check if windows nt os
if os.name == "nt":
    socket_protocol = socket.IPPROTO_IP
else:
    socket_protocol = socket.IPPROTO_ICMP

sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)

sniffer.bind((host, 0))
sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

if os.name == "nt":
    
    sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

try:
    
    while True:
        
        # read in a packet
        raw_buffer = sniffer.recvfrom(65565)[0]
        
        # create an IP header from the first 20 bytes after the buffer
        # changed to 32 because of from_buffer_copy ValueError
        ip_header = IP(raw_buffer[0:32])
               
        # print out the protocol that was detected and the hosts
        print("Protocol: %s %s -> %s" % (ip_header.protocol, ip_header.src_address, ip_header.dst_address))
        

# handle CTRL-C
except KeyboardInterrupt:
    
    # if we're using Windows, turn off promiscious mode
    if os.name == "nt":
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)