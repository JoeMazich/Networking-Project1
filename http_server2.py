import select
import socket
import sys

#!!!!!!!!!!!!!! BASE CODE STRUCTURE RECIEVED FROM https://pymotw.com/3/select/ !!!!!!!!!!!!!!!!!!!!!!!!!

port = int(sys.argv[1])

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((socket.gethostname(), port))
server.listen(5)

inputs = [server]
outputs = []

message_queues = {}

while inputs:
    # Recieved from https://pymotw.com/3/select/
    readable, writable, exceptional = select.select(inputs,outputs,inputs)
    # Handle inputs
    for s in readable:
        if s is server:
            connection, client_address = s.accept()
            inputs.append(connection)
            message_queues[connection] = []

        else:
            fullRequest = s.recv(4096).decode()

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
                        request = connection.recv(4096) # recieve the request with max of 4096 bits(?) at once
                        fullRequest += request.decode()
                except Exception as e:
                    while True:
                        request = connection.recv(4096)
                        fullRequest += request.decode()
                        if len(request.decode()) < 4096:
                            break

            if fullRequest:
                if header['HTTP-Command'] != 'GET':
                    fullResponse = 'HTTP/1.1 400 Bad Request\r\nContent-Length: 0\r\nContent-Type: text/html\r\n\r\n'
                elif not (header['Path'][-4:] == '.htm' or header['Path'][-5:] == '.html'):
                    fullResponse = 'HTTP/1.1 403 Forbidden\r\nContent-Length: 0\r\nContent-Type: text/html\r\n\r\n'
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
                message_queues[s].append(fullResponse)
                # Add output channel for response
                if s not in outputs:
                    outputs.append(s)
            else:
                # Interpret empty result as closed connection
                # Recieved from https://pymotw.com/3/select/
                if s in outputs:
                    outputs.remove(s)
                inputs.remove(s)
                s.close()
                del message_queues[s]
    # Handle outputs
    for s in writable:
        try:
            next_msg = message_queues[s][0]
            if len(message_queues[s]) == 1:
                message_queues[s] = []
            else:
                message_queues[s] = message_queues[s][1:]
            s.send(next_msg.encode())
        except IndexError:
            # No messages waiting so stop checking
            # for writability.
            outputs.remove(s)

    # Handle "exceptional conditions"
    for s in exceptional:
        # Recieved from https://pymotw.com/3/select/
        # Stop listening for input on the connection
        inputs.remove(s)
        if s in outputs:
            outputs.remove(s)
        s.close()
        del message_queues[s]
