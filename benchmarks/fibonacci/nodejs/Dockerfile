FROM node:stretch-slim

WORKDIR /app
COPY proto/helloworld.proto /app
COPY nodejs/* /app/
# COPY protos /app/proto

RUN npm install

ENTRYPOINT [ "node", "server.js" ]
