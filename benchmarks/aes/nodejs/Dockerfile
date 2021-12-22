FROM node:stretch-slim

WORKDIR /app
COPY * /app/
# COPY protos /app/proto

RUN npm install
# RUN npm config set registry http://registry.npm.taobao.org/ && npm install

ENTRYPOINT [ "node", "server.js" ]
