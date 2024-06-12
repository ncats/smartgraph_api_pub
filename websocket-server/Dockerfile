# NodeJS docker image for gateway
ARG NODE_IMAGE_VERSION=20.13.0-alpine
ARG PORT=${sg_websocket_server_port}

FROM node:${NODE_IMAGE_VERSION}

RUN apk add --update python3 make g++\
   && rm -rf /var/cache/apk/*

WORKDIR /usr/src/app
COPY . .
RUN chmod -R 777 /usr/src/app
RUN pwd
RUN ls -la

# Install app dependencies
RUN npm install

# Set to run as node user
USER node

# Expose and set run command
EXPOSE ${PORT}
CMD [ "node", "websocket-server.ts" ]
