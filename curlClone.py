import socket
import sys

# Super messy right now - just trying to get it done quick to move onto the next part

def curl(url, attempts):

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if url[0:7] != "http://":
        return('exit 1')

    host, port, path = parseURL(url)

    # Find IP
    host_IP = socket.gethostbyname(host)

    # Connect to host using the IP found via DNS and port vis the URL parse
    client.connect((host_IP, int(port)))

    request = "GET %s HTTP/1.0\r\nHost: %s\r\n\r\n" %(path, host)
    client.send(request.encode())

    fullResponse = client.recv(4096).decode()
    responseType = int(fullResponse.split(' ', 2)[1]) # spits out the HTTP response type (200, 302, 301, 400, 404, etc)

    # Makes anything else in the header 'easier' to digest
    header = {}
    for line in fullResponse.split('\n\r\n')[0].split('\n'):
        if ':' in line:
            x, y = line.split(':', 1)
            header[x] = y.strip()


    if responseType == 302 or responseType == 301:
        if attempts >= 10:
            return('exit 2')
        sys.stderr.write('Redirected to %s \n' %header['Location'])
        return curl(header['Location'], attempts + 1)

    elif responseType >= 400:
        return('exit 3')

    # this should the the last step after all (up to 10) redirects
    while len(fullResponse) < int(header['Content-Length']):
        response = client.recv(4096) # recieve the request with max of 4096 bits(?) at once
        fullResponse += response.decode()

    return fullResponse

    '''
    responsetype = int(fullResponse.split(' ', 2)[1])
    if responsetype == 200: # also need to check if contenttype is text/html
        print(fullResponse)
        return ('exit 0')
    elif responsetype >= 400:
        print(fullResponse)
        return ('exit 2')

    return fullResponse # parse this
    '''
    # We will always use HTTP GET, which will (i think) return if it is a redirect. This is how we
    # can deal with them. We must check for HTTP response above 400, content-type (must be text/html
    # if not a redirect).


def parseURL(url):
    longpath = url.split('//')[1]
    firstslash = longpath.find('/')

    if firstslash != -1:
        hostport = longpath[0:firstslash].split(':')
        path = longpath[firstslash:]
    else:
        hostport = longpath.split(':')
        path = None

    if len(hostport) == 2:
        host, port = hostport
    else:
        host = hostport[0]
        port = 80
    return host, port, path


if __name__ == "__main__":
    url = sys.argv[1]
    print(curl(url, 0))
