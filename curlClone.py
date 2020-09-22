import socket
import sys

# Super messy right now - just trying to get it done quick to move onto the next part

def curl():

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    url = sys.argv[1]

    # Parse input URL
    if url[0:7] != "http://":
        return("exit 1")

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

    # Find IP
    host_IP = socket.gethostbyname(host)

    # Connect to host using the IP found via DNS and port vis the URL parse
    client.connect((host_IP, int(port)))
    # Create the request
    request = "GET %s HTTP/1.0\r\nHost: %s\r\n\r\n" %(path, host)
    # Encode and send the request
    client.send(request.encode())

    fullResponse = ''
    for i in [1, 1, 1, 1]: # change into while loop the breaks with
        response = client.recv(4096) # recieve the request with max of 4096 bits(?) at once
        fullResponse += response.decode()

    responsetype = int(fullResponse.split(' ', 2)[1])
    if responsetype == 200: # also need to check if contenttype is text/html
        print(fullResponse)
        return ('exit 0')
    elif responsetype >= 400:
        print(fullResponse)
        return ('exit 2')

    return response # parse this

    # We will always use HTTP GET, which will (i think) return if it is a redirect. This is how we
    # can deal with them. We must check for HTTP response above 400, content-type (must be text/html
    # if not a redirect). Content-length check for another request - gotta figure this out later (comes into play for pages like libc.html)

    # Out

if __name__ == "__main__":
    print(curl())
