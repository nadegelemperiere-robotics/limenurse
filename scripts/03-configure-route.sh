#! /bin/bash
# -------------------------------------------------------
# Copyright (c) [2025] Nadege Lemperiere
# All rights reserved
# -------------------------------------------------------
# Configure a raspberry pi routes to :
# - Transfer all traffic from limeligth on eth1 to usb0 and reciprocally
# - Transfer all traffic from limeligth on eth1 to eth0 and reciprocally
# - Still enable ssh connection to the pi through eth0 
# -------------------------------------------------------
# Nadège LEMPERIERE, @2nd May 2025
# Latest revision: 2nd May 2025
# -------------------------------------------------------


# 0 - Retrieve absolute path to this script
script=$(readlink -f $0)
scriptpath=`dirname $script`

# 1 - Configure IP forwarding
echo ""
echo "❶ Configuring IP forwarding"

# Enable IP forwarding
SYSCTL_RULE=/etc/sysctl.d/99-ipforward.conf
echo "net.ipv4.ip_forward = 1" | sudo tee $SYSCTL_RULE
sysctl -p $SYSCTL_RULE

echo "  ➡️  Enabled IPv4 forwarding"

shall_reboot=false
source $scriptpath/../conf/env

echo ""
echo "❷ Configuring iptables rules"

# Installing iptables
apt -qq update
apt -qq install -y iptables
echo "  ➡️  Installed iptables"

# Creating iptables rules

source $scriptpath/../conf/env
export ROUTING_SCRIPT_PATH=/usr/local/bin/limelight-routing.sh

cp $scriptpath/../data/udp_forwarder.py /usr/local/bin/udp_forwarder.py

envsubst '$ETH_IP_GATEWAY,$USB_IP_GATEWAY' < $scriptpath/../data/limelight-routing.sh > $ROUTING_SCRIPT_PATH
chmod +x $ROUTING_SCRIPT_PATH

echo "  ➡️  Created limelight routing script"

SERVICE_PATH=/etc/systemd/system/limelight-routing.service
envsubst '$ROUTING_SCRIPT_PATH' < $scriptpath/../data/limelight-routing.service > $SERVICE_PATH

echo "  ➡️  Prepared limelight routing service"

# Check if service already exists
if systemctl list-unit-files | grep -q limelight-routing.service; then
    echo "  🔁 Service already exists. Reloading, enabling, and restarting."
    systemctl daemon-reload
    systemctl enable limelight-routing.service
    systemctl restart limelight-routing.service
else
    echo "  🆕 Installing new service."
    systemctl daemon-reload
    systemctl enable limelight-routing.service
    systemctl start limelight-routing.service
fi

if ! systemctl is-active --quiet limelight-routing.service; then
    echo "  ❌ Failed to start limelight routing service"
    exit 1
fi

echo "✅ Limelight routing installation complete"

# 4 - Reboot to make sure everything is consistent
echo ""
echo "✅ All routes available."
echo "🔄 Rebooting in 5 seconds... Press CTRL+C to cancel."
sleep 5
shutdown -r now