import socket
import sys

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind((socket.gethostname(), 1900))
s.listen(1)

print(socket.gethostname())

while True:
    clientSock, clientAddr = s.accept()
    clientSock.send(bytes("Welcome", "utf-8"))
