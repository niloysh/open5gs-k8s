FROM node:18-slim as builder

WORKDIR /open5gs

RUN apt-get update \
    && apt-get install -y git

RUN git clone -b v2.6.4 https://github.com/open5gs/open5gs .

WORKDIR /open5gs/webui

RUN npm ci && \
    npm run build

FROM node:18-slim

WORKDIR /open5gs/webui
COPY --from=builder /open5gs/webui/ /open5gs/webui/

RUN npm install --production

EXPOSE 3000
