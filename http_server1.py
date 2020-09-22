import socket
import sys

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind(('localhost', 1900))
s.listen(5)

while True:
    clientSock, clientAddr = s.accept()
    fullResponse = clientSock.recv(4096).decode()
    print(fullResponse)

    # Same header parsing as the curl clone
    header = {}
    for line in fullResponse.split('\n\r\n')[0].split('\n'):
        if ':' in line:
            x, y = line.split(':', 1)
            header[x] = y.strip()

    # Same loop to make sure we get all the data
    while len(fullResponse) < int(header['Content-Length']):
        response = client.recv(4096)
        fullResponse += response.decode()
