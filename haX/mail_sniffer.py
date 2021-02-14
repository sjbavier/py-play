#!/usr/bin/python3

from scapy.all import *

# out packet callback
def packet_callback(packet):
    if packet.payload.name == 'TCP':
        mail_packet = str(packet.payload.name)
        if 'user' in mail_packet.lower() or 'pass' in mail_packet.lower():
            print(f'[*] Source: {packet.src}')
            print(f'[*] Server Destination: {packet.dst}')
            print(f'[*] {packet.payload}')

    else:
        print(f'Packet Type: {packet.payload.name}')
        print(f'                 Src: {packet.src} ========> Dst: {packet.dst}')
        # print(packet.show())

def main():
    # fire up our sniffer
    sniff(prn=packet_callback,store=0)

if __name__ == '__main__': main()