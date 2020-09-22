import socket
import sys

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind((socket.gethostname(), 1900))

print(socket.gethostname())

while True:
    clientSocket, clientAddr = s.accept()
