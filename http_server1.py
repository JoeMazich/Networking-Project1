import socket
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

    try: # This is a very dumb thing to do but it keeps returning errors where it cannot find the client socket when
        try: # no request has benn made yet - be my guest to take this out and try it, let me know if it works for you
            while len(fullRequest) < int(header['Content-Length']):
                request = client.recv(4096) # recieve the request with max of 4096 bits(?) at once
                fullRequest += request.decode()
        except Exception as e:
            while True:
                request = client.recv(4096)
                fullRequest += request.decode()
                if len(request.decode()) < 10:
                    break
    except Exception as e:
        pass

    # Controlling all the request stuff here, pretty self explanatory
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
