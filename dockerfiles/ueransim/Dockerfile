FROM gcc:9.4.0 AS builder

LABEL maintainer="Niloy Saha <niloysaha.ns@gmail.com>"
LABEL description="UERANSIM v3.2.6"

ENV DEBIAN_FRONTEND noninteractive

# Install dependencies
RUN apt-get update \
    && apt-get install libsctp-dev lksctp-tools iproute2 -y \
    && wget https://github.com/Kitware/CMake/releases/download/v3.22.1/cmake-3.22.1-linux-x86_64.sh -O cmake_installer.sh \
    && chmod +x cmake_installer.sh \
    && ./cmake_installer.sh --skip-license \
    && git clone -b v3.2.6 -j `nproc` https://github.com/aligungr/UERANSIM \
    && cd ./UERANSIM \
    && make

FROM ubuntu:20.04

ENV DEBIAN_FRONTEND noninteractive

# Install runtime dependencies + debug tools
RUN apt-get update \
    && apt-get install libsctp-dev lksctp-tools iproute2 iputils-ping -y \
    && apt-get install vim iperf3 net-tools tcpdump -y \
    && apt-get clean

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