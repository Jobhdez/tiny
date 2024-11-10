import socket
import re
import os

HOST = "127.0.0.1"
PORT = 65432

def handle_request(data):
    method, uri, version = parse_request(data)

    match method:
        case 'GET':
            path = uri.strip('/')
            if not path:
                path = 'index.html'

            if os.path.exists(path) and not os.path.isdir(path):
                response_line = 'HTTP/1.1 200 OK\r\n'
                headers = ["Server: Manifold Server", "Content-Type: text/html\r\n"]
                
                with open(path, 'rb') as f:
                    body = f.read()

                header = "\r\n".join(headers).encode()
                response_line = response_line.encode()
                return b''.join([response_line, header, b'\r\n', body])

            response_line = 'HTTP/1.1 404 Not Found\r\n'
            headers = ["Server: Manifold Server", "Content-Type: text/html\r\n"]
            header = "\r\n".join(headers).encode()
            body = b'<h1>404 Not Found</h1>'
            response_line = response_line.encode()
            return b''.join([response_line, header, b'\r\n', body])
          
        case 'POST':
          key_val_pattern = rb'(\w+)=([^&\s]+)'
          data = re.findall(key_val_pattern, data)
          val = int(data[0][1].decode())
          val2 = int(data[1][1].decode())

          body = f"<h1> the result is {val+val2}</h1>"

          response_line = 'HTTP/1.1 200 OK\r\n'
          headers = ["Server: Manifold Server", "Content-Type: text/html\r\n"]
          header = "\r\n".join(headers).encode()
          response_line = response_line.encode()
          body = body.encode()
          return b''.join([response_line, header, b'\r\n', body])

        case _:
            response_line = 'HTTP/1.1 501 Not Implemented\r\n'
            headers = ["Server: Manifold Server", "Content-Type: text/html\r\n"]
            header = "\r\n".join(headers).encode()
            body = b'<h1>501 Not Implemented</h1>'
            response_line = response_line.encode()
            return b''.join([response_line, header, b'\r\n', body])

def parse_request(request):
    pattern = re.compile(rb"^GET|POST .+ HTTP/[0-9]*\.[0-9]+", re.MULTILINE)
    request_line = pattern.findall(request)[0]

    components = request_line.split(b' ')
    method = components[0].decode()
    uri = components[1].decode()
    http_version = components[2].decode()
    return method, uri, http_version

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print("Server is listening...")
    
    while True:
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            data = conn.recv(1024)
            if not data:
                break

            response = handle_request(data)
            print(f"Client says: {data.decode()}")
            conn.sendall(response)
        conn.close()
