FROM alpine:3.13.5

# Install python3
RUN apk add --no-cache py3-pip py3-grpcio py3-protobuf py3-psutil py3-numpy git && \
    ln -sf python3 /usr/bin/python && ln -sf pip3 /usr/bin/pip

WORKDIR /app
COPY *.py ./

# EXPOSE is primarily a no-op now.
EXPOSE 80

STOPSIGNAL SIGKILL

CMD ["python", "trace_func.py"]