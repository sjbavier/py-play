import socket

target_host = "www.google.com"
target_port = 80

# create a socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect the client
client.connect((target_host, target_port))

# encode string to bytes for socket object's send method (python 3+)
request_string = "GET / HTTP/1.1\r\nHost: google.com\r\n\r\n"
bytes_request = request_string.encode(encoding='utf-8',errors='strict')

# send GET request
client.send(bytes_request)

# receive response data with buffer size of 4096 bytes
response = client.recv(4096)

print(response)