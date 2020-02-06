#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# Copyright 2020 Jolene Poulin
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse
import time

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port_path(self,url):
        # Parse URL
        pr = urllib.parse.urlparse(url)
        host = pr.hostname
        port = pr.port or 80
        path = pr.path or '/'
        return host, port, path

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        split_data = data.split('\r\n')
        header = split_data[0]
        status_code = header.split()[1]
        return int(status_code)

    def get_headers(self,data):
        return data.split('\r\n\r\n')[0]

    def get_body(self, data):
        return data.split('\r\n\r\n')[1]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        # Parse url to get info
        host, port, path = self.get_host_port_path(url)
        
        # Establish connection
        self.connect(host, port)

        # Set standard, path, host, port, accept any data type, close connection
        package = f"GET {path} HTTP/1.1\r\n" + \
                f"Host: {host}:{port}\r\n" + \
                "Accept: */*\r\n" + \
                "Connection: close\r\n\r\n"

        self.sendall(package)

        # Receive data
        res = self.recvall(self.socket)
        self.close()

        # Send response data
        code = self.get_code(res)
        body = self.get_body(res)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
         # Parse url to get info
        host, port, path = self.get_host_port_path(url)
        
        # Establish connection
        self.connect(host, port)

        # Set standard, path, host, port, accept any data type, close connection
        package = f"POST {path} HTTP/1.1\r\n" + \
                f"Host: {host}:{port}\r\n" + \
                "Accept: */*\r\n" + \
                "Connection: close\r\n"

        if args:
            content = urllib.parse.urlencode(args)
            content_length = str(len(content))
            package += "Content-type: application/x-www-form-urlencode\r\n" + \
                        f"Content-length: {content_length}\r\n\r\n" + \
                        content
        else:
            package += "Content-length: 0\r\n\r\n"

        self.sendall(package)

        # Receive data
        res = self.recvall(self.socket)
        self.close()

        # Send response data
        code = self.get_code(res)
        body = self.get_body(res)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
