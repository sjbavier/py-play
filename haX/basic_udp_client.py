import socket

target_host = "127.0.0.1"
target_port = 80

# create socket object
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# encode string to bytes for socket object's send method (python 3+)
request_string = "abc"
bytes_request = request_string.encode(encoding='utf-8',errors='strict')

# send data
client.sendto(bytes_request, (target_host, target_port))

# receive some data
data, addr = client.recvfrom(4096)

print(data)