#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import socket
import ssl
import subprocess
# SET VARIABLES
HOST = socket.gethostbyname('wk-de-WallA-2X2QIW2LFXR1-1345292554.us-east-1.elb.amazonaws.com')
PORT = 443
# with open('sample-request2.txt', 'rb') as f:
with open('sample-request.txt', 'rb') as f:
    REQUEST = f.read()

exit_on_err = True


while True:
    # CREATE SOCKET
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    # WRAP SOCKET
    wrappedSocket = ssl.wrap_socket(
        sock,
        ssl_version=ssl.PROTOCOL_TLSv1_2,
        ciphers='ECDHE-RSA-AES128-GCM-SHA256'
    )
    # CONNECT AND PRINT REPLY
    wrappedSocket.connect((HOST, PORT))
    wrappedSocket.send(REQUEST)
    response = wrappedSocket.recv(1280)

    if response.startswith("HTTP/1.1 502"):
        print("Mangled Request:")
        print(response)
        if exit_on_err:
            break
    else:
        print("Request Okay")

    # CLOSE SOCKET CONNECTION
    wrappedSocket.close()
    time.sleep(.2)
