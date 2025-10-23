FROM --platform=$BUILDPLATFORM ubuntu:22.04 as builder

WORKDIR /open5gs

RUN apt-get update \
    && apt-get install -y curl git python3 make g++ \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

RUN git clone -b v2.7.0 https://github.com/open5gs/open5gs .

WORKDIR /open5gs/webui

RUN npm ci --no-optional && \
    npm run build

FROM --platform=$TARGETPLATFORM ubuntu:22.04

WORKDIR /open5gs/webui

RUN apt-get update \
    && apt-get install -y curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /open5gs/webui/ /open5gs/webui/

RUN npm ci --production --no-optional

EXPOSE 3000

CMD ["node", "app.js"]