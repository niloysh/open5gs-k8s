#!/bin/bash

mkdir /dev/net
mknod /dev/net/tun c 10 200

/ueransim/nr-ue -c /ueransim/config/ue3.yaml 