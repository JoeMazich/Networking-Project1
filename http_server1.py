import socket
import sys
import os

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind(('localhost', 1900))
s.listen(5)

def sendHeader(code, length, type):
    # rewrite into switch
    if code == 200:
        code = '200 OK'
    elif code == 400:
        code = '400 Bad Request'
    elif code == 403:
        code = '403 Forbidden'
    elif code == 404:
        code = '404 Not Found'
    return ('HTTP/1.1 %s \r\nContent-Length: %s\r\nContent-Tpye: \r\n\r\n' %(code, length, type))

while True:
    clientSock, clientAddr = s.accept()
    request = clientSock.recv(4096).decode()

    # Same header parsing as the curl clone
    header = {}
    firstLine = request.split('\n')[0].split(' ')
    header['HTTP-Command'] = firstLine[0]
    header['Path'] = firstLine[1]
    header['HTTP-Type'] = firstLine[2]
    for line in request.split('\n\r\n')[0].split('\n'):
        if ':' in line:
            x, y = line.split(':', 1)
            header[x] = y.strip()

    if header['HTTP-Command'] != 'GET':
        clientSock.send(sendHeader(400, 0, 'text/html').encode())
    else:
        try:
            file = open(header['Path'][1:], 'r')
            response = file.read()
            file.close()

            response = 'HTTP/1.1 200 OK \r\nContent-Length: %s\r\nContent-Type: text/html\r\n\r\n' %(len(response)) + response
            clientSock.send(response.encode())
        except Exception:
            clientSock.send('404'.encode())

    clientSock.close()
