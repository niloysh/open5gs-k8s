FROM ubuntu:22.04 AS builder

ENV DEBIAN_FRONTEND=noninteractive
ENV LD_LIBRARY_PATH=/open5gs/install/lib/x86_64-linux-gnu

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    python3-pip python3-setuptools python3-wheel \
    ninja-build build-essential flex bison git cmake \
    libsctp-dev libgnutls28-dev libgcrypt-dev libssl-dev \
    libidn11-dev libmongoc-dev libbson-dev libyaml-dev \
    libnghttp2-dev libmicrohttpd-dev libcurl4-gnutls-dev \
    libtins-dev libtalloc-dev meson

WORKDIR /open5gs

RUN git clone -b v2.6.6 https://github.com/open5gs/open5gs .

RUN meson build --prefix=/open5gs/install \
    && ninja -C build \
    && ninja -C build install

FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive
ENV LD_LIBRARY_PATH=/open5gs/install/lib/x86_64-linux-gnu

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    libsctp-dev libgnutls28-dev libgcrypt-dev libssl-dev \
    libidn11-dev libmongoc-dev libbson-dev libyaml-dev \
    libnghttp2-dev libmicrohttpd-dev libcurl4-gnutls-dev \
    libtins-dev libtalloc-dev ca-certificates \
    vim tcpdump iputils-ping iproute2 iptables \
    && apt-get autoremove -y && apt-get autoclean

RUN mkdir -p /open5gs/install
RUN update-ca-certificates

WORKDIR /open5gs/install/bin

COPY --from=builder /open5gs/install /open5gs/install
COPY --from=builder /open5gs/install/etc /etc/open5gs/

