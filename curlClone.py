import socket
import sys

# Super messy right now - just trying to get it done quick to move onto the next part

def curl(url, attempts):

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if url[0:8] == "https://":
        sys.stderr.write("https not supported\n")
        sys.exit(1)
    elif url[0:7] != "http://":
        sys.exit(1)

    host, port, path = parseURL(url)

    # Find IP
    host_IP = socket.gethostbyname(host)

    # Connect to host using the IP found via DNS and port vis the URL parse
    client.connect((host_IP, int(port)))

    request = "GET %s HTTP/1.0\r\nHost: %s\r\nContent-Length: 0\r\n\r\n" %(path, host)
    client.send(request.encode())

    fullResponse = client.recv(4096).decode()
    responseType = int(fullResponse.split(' ', 2)[1]) # spits out the HTTP response type (200, 302, 301, 400, 404, etc)

    # Makes anything else in the header 'easier' to digest
    header = {}
    for line in fullResponse.split('\n\r\n')[0].split('\n'):
        if ':' in line:
            x, y = line.split(':', 1)
            header[x] = y.strip()
    try:
        decodetype = header['Content-Type'].split('=')[1]
    except:
        decodetype = 'utf-8'

    # Redirection
    if responseType == 302 or responseType == 301:
        if attempts >= 10:
            sys.stderr.write('Too many redirects!!\n')
            sys.exit(2)
        sys.stderr.write('Redirected to %s \n' %header['Location'])
        client.close()
        return curl(header['Location'], attempts + 1)

    # We know it is not a redirect, so lets go ahead and grab everything from the page
    try:
        while len(fullResponse) < int(header['Content-Length']):
            response = client.recv(4096) # recieve the request with max of 4096 bits(?) at once
            fullResponse += response.decode('utf-8')
    except Exception as e:
        while True:
            response = client.recv(4096)
            fullResponse += response.decode('utf-8')
            if len(response.decode('utf-8')) < 10:
                break



    # Page error
    if responseType >= 400:
        sys.stdout.write(fullResponse)
        sys.exit(3)

    # Got the page
    elif responseType == 200:
        # make sure Content header is correct
        if header['Content-Type'].split(';')[0] == 'text/html':
            sys.stdout.write(fullResponse)
            sys.exit(0)
        else:
            sys.exit(4)

    sys.exit(5)

def parseURL(url):
    longpath = url.split('//')[1]
    firstslash = longpath.find('/')

    if firstslash != -1:
        hostport = longpath[0:firstslash].split(':')
        path = longpath[firstslash:]
    else:
        hostport = longpath.split(':')
        path = '/'

    if len(hostport) == 2:
        host, port = hostport
    else:
        host = hostport[0]
        port = 80
    return host, port, path


if __name__ == "__main__":
    url = sys.argv[1]
    print(curl(url, 0))
