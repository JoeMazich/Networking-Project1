import socket
import sys

port = int(sys.argv[1])

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind(('localhost', port))
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
    header = 'HTTP/1.1 %s \r\nContent-Length: %s\r\nContent-Type: \r\n\r\n' %(code, str(length), type)
    print(header)
    return header

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
        response = 'HTTP/1.1 400 Bad Request\r\nContent-Length: 0\r\nContent-Type: text/html\r\n\r\n'
        clientSock.send(response.encode())
    elif not (header['Path'][-4:] == '.htm' or header['Path'][-5:] == '.html'):
        response = 'HTTP/1.1 403 Forbidden\r\nContent-Length: 0\r\nContent-Type: text/html\r\n\r\n'
        clientSock.send(response.encode())
    else:
        try:
            file = open(header['Path'][1:], 'r')
            response = file.read()
            file.close()

            responselength = len(response)
            responsetype = 'text/html'
            exit_code = '200 OK'
        except Exception as e:
            response = ''
            responselength = 0
            responsetype = 'text/html'
            exit_code = '404 Not Found'

        fullResponse = 'HTTP/1.1 ' + exit_code + '\r\nContent-Length: ' + str(responselength) + '\r\nContent-Type: ' + responsetype +'\r\n\r\n' + response
        clientSock.send(fullResponse.encode())


    clientSock.close()
