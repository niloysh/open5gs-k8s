FROM ubuntu:22.04 AS builder
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip python3-setuptools python3-wheel \
    ninja-build build-essential flex bison git cmake meson \
    libsctp-dev libgnutls28-dev libgcrypt-dev libssl-dev \
    libidn11-dev libmongoc-dev libbson-dev libyaml-dev \
    libnghttp2-dev libmicrohttpd-dev libcurl4-gnutls-dev \
    libtins-dev libtalloc-dev pkg-config ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /open5gs
RUN git clone -b v2.7.0 https://github.com/niloysh/open5gs .

RUN meson build --prefix=/open5gs/install \
 && ninja -C build \
 && ninja -C build install

# Register libs so RPATH/LD_LIBRARY_PATH is unnecessary
RUN echo "/open5gs/install/lib" > /etc/ld.so.conf.d/open5gs.conf && \
    arch_dir="$(dpkg-architecture -qDEB_HOST_MULTIARCH || true)" && \
    [ -d "/open5gs/install/lib/${arch_dir}" ] && echo "/open5gs/install/lib/${arch_dir}" >> /etc/ld.so.conf.d/open5gs.conf || true && \
    ldconfig

FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive

# Runtime libs only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsctp1 libgnutls30 libgcrypt20 libssl3 \
    libidn12 libmongoc-1.0-0 libbson-1.0-0 libyaml-0-2 \
    libnghttp2-14 libmicrohttpd12 libcurl4 libtins4.0 \
    libcurl3-gnutls libtalloc2 ca-certificates \
    vim tcpdump iputils-ping iproute2 iptables && \
    rm -rf /var/lib/apt/lists/* && update-ca-certificates

RUN mkdir -p /open5gs/install

# Copy artifacts
COPY --from=builder /open5gs/install /open5gs/install
COPY --from=builder /open5gs/install/etc /etc/open5gs/

# Register library paths (multi-arch safe)
RUN echo "/open5gs/install/lib" > /etc/ld.so.conf.d/open5gs.conf && \
    arch_dir="$(dpkg-architecture -qDEB_HOST_MULTIARCH || true)" && \
    [ -d "/open5gs/install/lib/${arch_dir}" ] && echo "/open5gs/install/lib/${arch_dir}" >> /etc/ld.so.conf.d/open5gs.conf || true && \
    ldconfig

WORKDIR /open5gs/install/bin
