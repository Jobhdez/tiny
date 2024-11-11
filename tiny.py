import socket
import re
import os
from urllib.parse import parse_qs
HOST = "127.0.0.1"
PORT = 65432

def handle_request(data):
    try:
        method, uri, version = parse_request(data)
    except ValueError as e:
        print(f"Error parsing request: {e}")
        return build_response("400 Bad Request", f"<h1>400 Bad Request:{e}</h1>")

    match method:
        case 'GET':
            path = uri.strip('/')
            if not path:
                path = 'index.html'

            if os.path.exists(path) and not os.path.isdir(path):
                with open(path, 'rb') as f:
                    body = f.read()
                return build_response("200 OK", body, "text/html")

            return build_response("404 Not Found", "<h1>404 Not Found</h1>")

        case 'POST':
            print(data)
            #key_val_pattern = rb'(\w+)=([^&\s]+)'
            #key_val_pattern = rb'(\w+)=([^&\s]+)'

            #data = re.findall(key_val_pattern, data)
            #print(data)
            data = parse_qs("num1=2&num2=4")
            print(data)
            try:
                val = int(data['num1'][0])
                val2 = int(data['num2'][0])
                body = f"<h1>The result is {val + val2}</h1>"
                return build_response("200 OK", body)
            except  ValueError as e:
                return build_response("400 Bad Request :)", f"<h1>400 Bad Request{e}</h1>")
            """body_data = data.split(b"\r\n\r\n", 1)[-1]
            parsed_data = parse_qs(body_data.decode())
            print(parsed_data)
            try:
              val1 = int(parsed_data.get("num1", [0])[0])
              val2 = int(parsed_data.get("num2", [0])[0])
              body = f"<h1>The result is {val1 + val2}</h1>"
              return build_response("200 OK", body)
            except (ValueError, TypeError):
              return build_response("400 Bad Request :)", "<h1>400 Bad Request</h1>")"""

        case _:
            return build_response("501 Not Implemented", "<h1>501 Not Implemented</h1>")

def parse_request(request):
    request_line_pattern = re.compile(rb"^(GET|POST) .+ HTTP/[0-9.]+")
    match = request_line_pattern.search(request)
    if not match:
        raise ValueError("Invalid request line")
    request_line = match.group().decode()
    components = request_line.split(" ")
    return components[0], components[1], components[2]

def build_response(status, body, content_type="text/html"):
    response_line = f"HTTP/1.1 {status}\r\n"
    headers = [
        "Server: Manifold Server",
        f"Content-Type: {content_type}\r\n",
    ]
    header = "\r\n".join(headers).encode()
    response_line = response_line.encode()
    body = body.encode() if isinstance(body, str) else body
    return b''.join([response_line, header, b'\r\n', body])


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
            print(f"Client says: {data.decode(errors='ignore')}")
            conn.sendall(response)
