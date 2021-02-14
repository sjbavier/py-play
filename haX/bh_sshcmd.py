import threading
import paramiko
import subprocess
import sys

# Usage: this script simply connects to an ssh server and executes a given command

def ssh_command(ip, ssh_port, user, passwd, command):
    
    # create the ssh client using paramiko library
    client = paramiko.SSHClient()

    #  load hostkeys from the known_hosts file
    client.load_host_keys('/home/sjbavier/.ssh/known_hosts')
    
    # set the policy for updating host keys
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    # connect to ip with username and password from arguments
    client.connect(ip, port=ssh_port, username=user, password=passwd)
    
    # using client get the transport object and
    # request new session from server
    ssh_session = client.get_transport().open_session()
    
    # if the session is active
    if ssh_session.active:

        #execute the command from arguments
        ssh_session.exec_command(command)

        # print the received data in utf-8
        print(ssh_session.recv(1024).decode("utf-8"))
    return

# incorportate CLI arguments            
server = sys.argv[1]
ssh_port = int(sys.argv[2])
user = sys.argv[3]
passwd = sys.argv[4]
command = sys.argv[5]

ssh_command(server, ssh_port , user, passwd, command)