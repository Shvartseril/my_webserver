import socket
from typing import Tuple, Union


class HttpRequest:
    def __init__(self, request: str):
        print(f'//{request}/!/')
        request_lines = request.split('\n')
        self.request: str = request
        self.start_line = request_lines[0]
        start_parts = self.start_line.split()
        self.method = start_parts[0]
        self.URI = start_parts[1]
        self.version = start_parts[2]
        self.headers = {}
        self.body = ''
        for line in request_lines[1:]:
            line = line.strip()
            if len(line) == 0:
                break
            line = line.split(': ')
            self.headers[line[0]] = line[1]
        for line in request_lines[::-1]:
            if len(line) == 0:
                break
            self.body = line + '\n' + self.body

    def __repr__(self):
        return f'method = {self.method}, URI = {self.URI}, version = {self.version}\n' \
               f'headers = {self.headers}\n' \
               f'body = {self.body}'


def generate_response(protocol: str, code: Union[str, int], status: str, headers: dict[str, str], body: str):
    headers_representation = ''
    for key, value in headers.items():
        headers_representation += key + ': ' + value + '\r\n'
    return f'{protocol} {code} {status}\r\n' \
           f'{headers_representation}' \
           '\r\n' \
           f'{body}'


class Router:
    def __init__(self):
        self.routes: dict[Tuple[str, str], callable] = {}
        self.arr_routes: dict[Tuple[str, str], callable] = {}

    def route(self, method: str, URI: str):
        def decorator(f: callable):
            self.routes[method, URI] = f
            return f

        return decorator

    def arr_route(self, method: str, start_URI: str):
        def decorator(f: callable):
            self.arr_routes[method, start_URI] = f
            return f
        return decorator

    def handle_request(self, request: HttpRequest):
        method = request.method
        headers: dict[str, str] = {'Server': 'custom', 'Content-Type': 'text/html; charset=UTF-8', 'Content-Language': 'ru'}
        if self.routes.get((request.method, request.URI)):
            body = self.routes[(method, request.URI)](request, headers)
            headers['Content-Length'] = str(len(body))
            return generate_response('HTTP/1.1', '200', 'OK', headers, body)
        else:
            for URI, func in self.arr_routes.items():
                if request.URI.startswith(URI):
                    body = func(request, headers)
                    headers['Content-Length'] = str(len(body))
                    return generate_response('HTTP/1.1', '200', 'OK', headers, body)
            headers['Content-Length'] = '0'
            return generate_response('HTTP/1.1', '404', 'Not Found', headers, '')


class Application:
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port
        self.router = Router()

    def run(self):
        server_socket = socket.socket()
        server_socket.bind((self.ip, self.port))
        server_socket.listen(1)
        connection, d = server_socket.accept()
        while True:
            request = connection.recv(2048)
            request = request.decode()
            request = HttpRequest(request)
            send_me = self.router.handle_request(request).encode()
            print(send_me)
            connection.send(send_me)