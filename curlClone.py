import socket
import sys

def main():
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
        print("Socket creation error: %s" %(socket.error))

    url = sys.argv[1]

    # Parse input URL
    if url[0:7] != "http://":
        return("Error, url must begin with http://")

    longpath = url.split('//')[1]
    firstslash = longpath.find('/')

    if firstslash != -1:
        hostport = longpath[0:firstslash].split(':')
        path = longpath[firstslash:len(longpath)]
    else:
        hostport = longpath.split(':')
        path = None

    if len(hostport) == 2:
        host, port = hostport
    else:
        host = hostport[0]
        port = 80
    # End of parse input URL

    # Connect to DNS
    try:
        host_IP = socket.gethostbyname(host)
    except socket.herror:
        print("Error finding host: %s" %(socket.herror))

    print(host_IP) # print IP of host for debugging

    client.connect((host_IP, port)) # connect to host using the IP found via DNS and port vis the URL parse

    request = "GET %s HTTP/1.0\r\nHost: %s\r\n\r\n" %(path, host) # create the request
    client.send(request.encode()) # encode and send the request

    response = client.recv(4096) # recieve the request with max of 4096 bits(?) at once
    print(response) # parse this



    # Return from server
    # We will always use HTTP GET, which will (i think) return if it is a redirect. This is how we
    # can deal with them. We must check for HTTP response above 400, content-type (must be text/html
    # if not a redirect). [Ignore Content-length? I think this will be clearer (for me) once we get to it]

    # Out

if __name__ == "__main__":
    main()
