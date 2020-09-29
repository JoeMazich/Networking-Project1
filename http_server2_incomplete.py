import select
import socket
import sys
import queue

port = int(sys.argv[1])

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #the accept socket
s.setblocking(0)

s.bind((socket.gethostname(), port))
s.listen(5)

read_list = [s]
write_list = []
message_queues = {}

while True:
    readable, writable, exceptional = select.select(read_list, write_list, read_list)
    #Note: This code, as well as several other parts of this script, were taken from https://pymotw.com/3/select/

    for readable_socket in readable:
        if readable_socket is s:
            clientSock, clientAddr = s.accept()
            clientSock.setblocking(0)
            read_list.append(clientSock)
            message_queues[clientSock] = queue.Queue()
        else:
            fullRequest = readable_socket.recv(4096).decode()
            if fullRequest: #got data
                if readable_socket not in write_list:
                    write_list.append(readable_socket)

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
                            if len(request.decode()) < 4096:
                                break


                # Controlling all the request stuff here, pretty self explanatory
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
                message_queues[readable_socket].put(fullResponse)
            else: #didn't get data
                if readable_socket in write_list:
                    write_list.remove(readable_socket)
                read_list.remove(readable_socket)
                readable_socket.close()
                del message_queues[readable_socket]

    for writable_socket in writable:
        try:
            next_message = message_queues[writable_socket].get_nowait()
            writable_socket.send(next_message.encode())
        except queue.Empty:
            write_list.remove(writable_socket)

    for exceptional_socket in exceptional:
        if exceptional_socket in write_list:
            write_list.remove(exceptional_socket)
        read_list.remove(exceptional_socket)
        exceptional_socket.close()
        del message_queues[exceptional_socket]
