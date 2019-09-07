#!/bin/bash

CLIENT_IP=192.168.23.22

FIREWALL_IP=192.168.23.$1

HAPROXY_IP=192.168.23.$2
DPORT=80

echo ""
echo "######################################"
echo "CLIENT_IP     FIREWALL_IP   HAPROXY_IP"
echo $CLIENT_IP   $FIREWALL_IP   $HAPROXY_IP 
echo "######################################"
echo ""

iptables -F
sudo iptables -t nat -F

iptables -t nat -A POSTROUTING -j MASQUERADE
iptables -t nat -A PREROUTING \! -s $CLIENT_IP -p tcp --dport $DPORT -j DNAT --to-destination $FIREWALL_IP:80
iptables -t nat -A PREROUTING -s $CLIENT_IP -p tcp --dport $DPORT -j DNAT --to-destination $HAPROXY_IP:80


sudo iptables -t nat -L -v
