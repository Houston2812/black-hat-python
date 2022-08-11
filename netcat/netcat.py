import argparse
from netrc import NetrcParseError
import socket
import shlex
import subprocess
import sys
import textwrap
import threading
from urllib import response

def execute(cmd):
    cmd = cmd.strip()
    if not cmd:
        return

    output = subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT)

    return output.decode()

class NetCat:
    def __init__(self, args, buffer=None) -> None:
        self.args = args
        self.buffer = buffer
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def run(self):
        if self.args.listen:
            self.listen()
        else:
            self.send()

    def send(self):
        # connect to target
        self.socket.connect((self.args.target, self.args.port))
        if self.buffer:
            self.socket.send(self.buffer)
        
        try:
            while True:
                recv_len = 1
                response = ''
                while recv_len:
                    data = self.socket.recv(4096)
                    recv_len = len(data)
                    response += data.decode()
                    if recv_len < 4096:
                        # stop the loop if no more data could be received
                        break
                if response:
                    print(response)
                    # receive the interactive input and continue the loop
                    try:
                        buffer = input('> ')
                        buffer += "\n"
                        self.socket.send(buffer.encode())
                    except EOFError:
                        print("Received")
                        
        except KeyboardInterrupt:
            # if user terminates the program with CTRL + C, close the connection
            print('User terminated')
            self.socket.close()
            sys.exit()

    def listen(self):
        self.socket.bind((self.args.target, self.args.port))
        self.socket.listen(5)

        while True:
            # waiting for the connections
            client_socket, _ = self.socket.accept()
            client_thread = threading.Thread(
                # passing the connected socket to the handle method
                target = self.handle, args = (client_socket, )
            )
            client_thread.start()

    def handle(self, client_socket):
        # executes the command sent to the listener
        if self.args.execute:
            output = execute(self.args.execute)
            client_socket.send(output.encode())

        # receives all data from a connection and writes to the buffer
        elif self.args.upload:
            file_buffer = b''
            while True:
                data = client_socket.recv(4096)
                if data:
                    file_buffer += data
                else:
                    break
            
            with open(self.args.upload, 'wb') as f:
                f.write(file_buffer)

            message = f'Saved file {self.args.upload}'
            client_socket.send(message.encode())


        # creates a shell
        elif self.args.command:
            cmd_buffer = b''
            # receives all commands in the loop and executes them 
            print('Hi')
            while True:
                try:
                    client_socket.send(b'BHPL: #> ')
                    # end of string check and make it more netcat friendly
                    while '\n' not in cmd_buffer.decode():
                        cmd_buffer += client_socket.recv(64)
                    response = execute(cmd_buffer.decode())
                    # return the response
                    if response:
                        client_socket.send(response.encode())
                    cmd_buffer = b''
                except Exception as e:
                    print(f'server killed {e}')
                    self.socket.close()
                    sys.exit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="BHP Net Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent('''Example:
            netcat.py -t 192.168.1.108 -p 5555 -l -c # command shell
            netcat.py -t 192.168.1.108 -p 5555 -l -u=mytest.txt # upload to file
            netcat.py -t 192.168.1.108 -p 5555 -l -e=\"cat /etc/passwd\" # execute command
            echo 'ABC' | ./netcat.py -t 192.168.1.108 -p 135 # echo text to server port 135
            netcat.py -t 192.168.1.108 -p 5555 # connect to server
        '''))
    parser.add_argument('-c', '--command', action='store_true', help='command shell')
    parser.add_argument('-e', '--execute', help='execute specified command')
    parser.add_argument('-l', '--listen', action='store_true', help='listen')
    parser.add_argument('-p', '--port', type=int, default=5555, help='speicifed port')
    parser.add_argument('-t', '--target', default='192.168.1.203', help='specified IP')
    parser.add_argument('-u', '--upload', help='upload file')

    # the -c, -e-, -u imply -l arguent -> applied only to listener 
    # -t, -p -> applied to sender to define the target listener

    args = parser.parse_args()

    if args.listen:
        # if we are listener NetCat object is envoked with empty buffer string
        buffer = ''
    else:
        buffer = sys.stdin.read()

    nc = NetCat(args, buffer.encode())

    nc.run()