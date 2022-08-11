import socket

target_host = "127.0.0.1"
target_port = 9998

# create a socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# AF_INET -> IPv5
# SOCK_STREAM -> TCP Client

# connect the client
client.connect((target_host, target_port))

# send some data
# client.send(b"GET / HTT/1.1\r\nHost: google.com\r\n\r\n")
client.send(b"AAABBBCCC")

response = client.recv(4096)

print(response.decode())
client.close()