import socket
import json
import sys

port = int(sys.argv[1])

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind((socket.gethostname(), port))
s.listen(5)

while True:
    clientSock, clientAddr = s.accept()
    fullRequest = clientSock.recv(4096).decode()

    # Same header parsing as the curl clone
    header = {}
    firstLine = fullRequest.split('\n')[0].split(' ')
    header['HTTP-Command'] = firstLine[0]
    header['Path'] = firstLine[1]
    header['HTTP-Type'] = firstLine[2]
    for line in fullRequest.split('\n\r\n')[0].split('\n'):
        if ':' in line:
            x, y = line.split(':', 1)
            header[x] = y.strip()

    if len(fullRequest) == 4096:
        try:
            while len(fullRequest) < int(header['Content-Length']):
                request = clientSock.recv(4096) # recieve the request with max of 4096 bits(?) at once
                fullRequest += request.decode()
        except Exception as e:
            while True:
                request = clientSock.recv(4096)
                fullRequest += request.decode()
                if len(request.decode()) < 10:
                    break

    # Controlling all the request stuff here, pretty self explanatory
    if header['HTTP-Command'] != 'GET':
        response = 'HTTP/1.1 400 Bad Request\r\nContent-Length: 0\r\nContent-Type: text/html\r\n\r\n'
        clientSock.send(response.encode())
    elif header['Path'][:8] != '/product':
        response = 'HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\nContent-Type: text/html\r\n\r\n'
        clientSock.send(response.encode())

    try:
        productList = header['Path'][9:].split('&')
    except:
        response = 'HTTP/1.1 400 Bad Request\r\nContent-Length: 0\r\nContent-Type: text/html\r\n\r\n'
        clientSock.send(response.encode())

    answer = 1
    operands = []
    for item in productList:
        try:
            answer = answer * float(item.split('=')[1])
            operands.append(float(item.split('=')[1]))
        except:
            response = 'HTTP/1.1 400 Bad Request\r\nContent-Length: 0\r\nContent-Type: text/html\r\n\r\n'
            clientSock.send(response.encode())
            break

    responsebody = json.dumps({'operation': 'product', 'operands': operands, 'result': answer}, indent=4)
    responseLength = len(responsebody)

    fullResponse = 'HTTP/1.1 200 OK\r\nContent-Length: ' + str(responseLength) + '\r\nContent-Type: application/json\r\n\r\n' + responsebody
    clientSock.send(fullResponse.encode())

    clientSock.close()
