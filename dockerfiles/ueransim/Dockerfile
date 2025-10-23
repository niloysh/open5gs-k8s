FROM --platform=$BUILDPLATFORM ubuntu:22.04 AS builder

LABEL maintainer="Niloy Saha <niloysaha.ns@gmail.com>"
LABEL description="UERANSIM v3.2.6"

ENV DEBIAN_FRONTEND=noninteractive

# Install build dependencies
RUN apt-get update && apt-get install -y \
    cmake \
    gcc \
    g++ \
    libsctp-dev \
    lksctp-tools \
    iproute2 \
    git \
    make \
    && rm -rf /var/lib/apt/lists/*

# Build UERANSIM
RUN git clone -b v3.2.6 -j $(nproc) https://github.com/aligungr/UERANSIM \
    && cd ./UERANSIM \
    && make

FROM --platform=$TARGETPLATFORM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    libsctp1 \
    lksctp-tools \
    iproute2 \
    iputils-ping \
    python3 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /ueransim

RUN mkdir -p config/ binder/

COPY /app/* ./
RUN chmod +x init.sh

COPY --from=builder /UERANSIM/build/nr-gnb .
COPY --from=builder /UERANSIM/build/nr-ue .
COPY --from=builder /UERANSIM/build/nr-cli .
COPY --from=builder /UERANSIM/build/nr-binder binder/
COPY --from=builder /UERANSIM/build/libdevbnd.so binder/

VOLUME [ "/ueransim/config" ]