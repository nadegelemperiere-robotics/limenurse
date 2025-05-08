#!/bin/bash
set -e

echo ""
echo "❶ Flushing old iptables rules..."

iptables -F
iptables -t nat -F
iptables -X
echo "   ✅ Flushed."

echo ""
echo "❷ Enabling IP forwarding"

sysctl -w net.ipv4.ip_forward=1 > /dev/null
echo "   ✅ Enabled."

echo ""
echo "❸ Adding DNAT rule for all traffic from usb0 and eth0 → Limelight on eth1"

iptables -t nat -A PREROUTING -i usb0 -d $USB_IP_GATEWAY -j DNAT --to-destination 172.29.0.1
iptables -t raw -A PREROUTING -i usb0 -p tcp --dport 22 -j DROP
iptables -t nat -A PREROUTING -i eth0 -d $ETH_IP_GATEWAY -p tcp ! --dport 22 -j DNAT --to-destination 172.29.0.1
echo "   ✅ PREROUTING rule set."

echo ""
echo "❹ Enabling FORWARDING rules between usb0 and eth1 and eth0 and eth1"

iptables -A FORWARD -i usb0 -o eth1 -j ACCEPT
iptables -A FORWARD -i eth0 -o eth1 -j ACCEPT
iptables -A FORWARD -i eth1 -o usb0 -m state --state RELATED,ESTABLISHED -j ACCEPT
iptables -A FORWARD -i eth1 -o eth0 -m state --state RELATED,ESTABLISHED -j ACCEPT

echo "   ✅ Forwarding rules set."

echo ""
echo "❺ Adding POSTROUTING MASQUERADE (if Limelight needs it)..."

iptables -t nat -A POSTROUTING -o eth1 -j MASQUERADE

echo "   ✅ MASQUERADE set."

echo "❻ Launching UDP forwarders"
python3 /usr/local/bin/udp_forwarder.py --from-ip1 $USB_IP_GATEWAY  --from-ip2 $ETH_IP_GATEWAY --from-interface1 usb0 --from-interface2 eth0 --to-ip 172.29.0.1 --to-interface eth1 > /var/log/udp_forwarder.log 2>&1 &  # usb0

echo "   ✅ UDP forwarders started"

echo ""
echo "✅ All rules successfully configured!"