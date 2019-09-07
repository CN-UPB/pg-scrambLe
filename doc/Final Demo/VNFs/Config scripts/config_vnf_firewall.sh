#!/bin/bash

HAPROXY_IP=192.168.23.$1
DPORT=80

echo ""
echo "######################################"
echo "HAPROXY_IP"
echo $HAPROXY_IP 
echo "######################################"
echo ""

iptables -F
iptables -t nat -F

iptables -t nat -A POSTROUTING -j MASQUERADE
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT
iptables -A INPUT -j DROP

iptables -t nat -A PREROUTING -p tcp --dport $DPORT -j DNAT --to-destination $HAPROXY_IP:80

iptables -t nat -L -v
