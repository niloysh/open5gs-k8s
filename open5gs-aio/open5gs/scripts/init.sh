#!/bin/bash   
ip tuntap add name ogstun mode tun;
ip addr add 10.45.0.1/16 dev ogstun;
sysctl -w net.ipv6.conf.all.disable_ipv6=1;
ip link set ogstun up;
sh -c "echo 1 > /proc/sys/net/ipv4/ip_forward";
iptables -t nat -A POSTROUTING -s 10.45.0.0/16 ! -o ogstun -j MASQUERADE;

sleep 604800