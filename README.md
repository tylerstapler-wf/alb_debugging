# ALB Debugging

This repo contains payloads and scripts which reproduce an ALB bug we have been experiencing.

In the normal case ALBs will take a chunked request, load all of the chunks into memory, and forward the full request to the backend. We're seeing that when the ALB is under load, some of these chunked requests are forwarded to the backend as chunked request but missing sizes on each of the chunks.

## Running the script

You will need to have `python` installed on your machine (2 or 3). Alternatively you can use docker to run the script.

**Shell**:

```shell
$ ./replay_request.py --help
usage: replay_request.py [-h] [--payload PAYLOAD] [--forever]
                         [--target TARGET]

optional arguments:
  -h, --help         show this help message and exit
  --payload PAYLOAD  The request to replay
  --forever          Run forever if set
  --target TARGET
```

**Docker**:
```shell
docker build . -t alb_debugging && docker run --rm -it alb_debugging
```

Running the ./replay_request.py script will open a TLS socket to the ALB and write a captured HTTP payload from a file (sample-request.txt) then close the socket. 

The expected response is 401 errors (We changed the auth tokens in the request to all Xs). The script will continue sending requests to the ALB until it encounters a 502 error, it will then print the error and exit.

```
$ ./replay_request.py
Connecting to 34.224.209.175:443
Request 1 Okay
Connecting to 52.207.124.20:443
Request 2 Okay
Connecting to 34.224.209.175:443
Request 3 Mangled:
HTTP/1.1 502 Bad Gateway
Server: awselb/2.0
Date: Fri, 22 Jun 2018 16:58:09 GMT
Content-Type: text/html
Content-Length: 138
Connection: keep-alive

<html>
<head><title>502 Bad Gateway</title></head>
<body bgcolor="white">
<center><h1>502 Bad Gateway</h1></center>
</body>
</html>
```

## Request Timeline
![Request Timeline](./ALB_request_timeline.png)


| Requests   | Explanations                                                                                                        |
|------------|---------------------------------------------------------------------------------------------------------------------|
|            |                                                                                                                     |
| Request A  | sample-request.txt                                                                                                  |
| Request B  | sample-request.txt with “Transfer Encoding: chunked” replaced with “Content-Length: 16428” and chunk sizes removed. |
| Request C  | sample-request.txt with “Transfer Encoding: chunked” header, but chunk sizes removed.                               |
| Response X | Expected 401 Response from our backend (HAProxy)                                                                    |
| Response Y | 502 Response from ALB                                                                                               |

## Repo Files
| File Name                              | Explanation                                                                                                                                                                                                                                           |
|----------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| replay_request.py                      | A python script for replaying HTTP requests                                                                                                                                                                                                           |
| sample-request.txt                     | A raw HTTP request which received a 502 response.                                                                                                                                                                                                     |
| sample-request-without-chunk-sizes.txt | A raw HTTP request which received a 502 response with the chunk sizes removed. This request is intended to demonstrate that the payload the ALB forwards to our backend is invalid. If you send it to the ALB you will get a "400 Bad Request error". |
