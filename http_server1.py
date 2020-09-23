import socket
import sys

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
    fullResponse = clientSock.recv(4096).decode()

    # This is such a hacky way to do this, really want to change this (working as a Connection detector)
    if len(fullResponse) > 0:
        # Same header parsing as the curl clone
        header = {}
        firstLine = fullResponse.split('\n')[0].split(' ')
        header['HTTP-Command'] = firstLine[0]
        header['Path'] = firstLine[1]
        header['HTTP-Type'] = firstLine[2]
        for line in fullResponse.split('\n\r\n')[0].split('\n'):
            if ':' in line:
                x, y = line.split(':', 1)
                header[x] = y.strip()

        '''# Same loop to make sure we get all the data
        while len(fullResponse) < int(header['Content-Length']):
            response = client.recv(4096)
            fullResponse += response.decode()'''

        if header['HTTP-Command'] != 'GET':
            clientSock.send(sendHeader(400, 0, 'text/html').encode())
        else:
            print(header['Path'])
