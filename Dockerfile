FROM python:2.7

COPY replay_request.py sample-request.txt sample-request-without-chunk-sizes.txt /

ENTRYPOINT /replay_request.py
