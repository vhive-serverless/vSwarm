FROM node:stretch-slim

WORKDIR /app
COPY nodejs/* /app/

# COPY protos /app/proto

RUN npm install
# RUN npm config set registry https://registry.npm.taobao.org/ && npm install

ENTRYPOINT [ "node", "server.js" ]
