import socket

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error:
    print("Socket creation error: %s" %(socket.error))

# url = input()

# Parse out url
# Need to look out for port, https, pull the host name (ignoring slashes), path and .html page

port = 80
host = "insecure.stevetarzia.com"

try:
    host_IP = socket.gethostbyname(host)
except socket.herror:
    print("Error finding host: %s" %(socket.herror))

print(host_IP)

s.connect((host_IP, port))

request = "GET /basic.html HTTP/1.0\r\nHost: %s\r\n\r\n" %(host)
s.send(request.encode())

response = s.recv(4096)
print(response) # parse this


# Return from server
# We will always use HTTP GET, which will (i think) return redirects. This is how we
# can deal with them. We must check for HTTP response above 400, content-type (must be text/html
# if not a redirect). Ignore Content-length?

# Out
