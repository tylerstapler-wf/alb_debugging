#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import socket
import ssl
import sys
import time

parser = argparse.ArgumentParser()
parser.add_argument(
    '--payload',
    dest="payload",
    default="sample-request.txt",
    help="The request to replay")

parser.add_argument(
    '--forever', dest="forever", action='store_true', help="Run forever")

parser.add_argument(
    '--target',
    dest="target",
    default='wk-de-WallA-2X2QIW2LFXR1-1345292554.us-east-1.elb.amazonaws.com')

args = parser.parse_args()

port = 443

with open(args.payload, 'rb') as f:
    request = f.read()

# Change this to False to run the script forever
REQUEST_PRINT_TEMPLATE = "Request {} {}"

run_forever = args.forever
request_count = 1

# Get all the ips assocated with hostname
hostname, aliaslist, ipaddrlist = socket.gethostbyname_ex(args.target)

while True:
    for ip in ipaddrlist:
        # CREATE SOCKET
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        # WRAP SOCKET
        wrappedSocket = ssl.wrap_socket(
            sock,
            ssl_version=ssl.PROTOCOL_TLSv1_2,
            ciphers='ECDHE-RSA-AES128-GCM-SHA256')
        # CONNECT AND PRINT REPLY
        print("Connecting to {}:{}".format(ip, port))
        wrappedSocket.connect((ip, port))
        wrappedSocket.send(request)
        response = wrappedSocket.recv(1280)

        if response.startswith(b"HTTP/1.1 502"):
            print(REQUEST_PRINT_TEMPLATE.format(request_count, "Mangled:"))
            print(response)
            if not run_forever:
                sys.exit(1)
        elif response.startswith(b"HTTP/1.1 400"):
            print(REQUEST_PRINT_TEMPLATE.format(request_count, "Rejected:"))
            print(response)
            if not run_forever:
                sys.exit(1)
        else:
            print(REQUEST_PRINT_TEMPLATE.format(request_count, "Okay"))

        # CLOSE SOCKET CONNECTION
        wrappedSocket.close()
        request_count += 1
        time.sleep(.2)
