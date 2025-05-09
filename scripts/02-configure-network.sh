#! /bin/bash
# -------------------------------------------------------
# Copyright (c) [2025] Nadege Lemperiere
# All rights reserved
# -------------------------------------------------------
# Configure a raspberry pi networks to manage different
# behaviour on its interfaces :
# - DHCP server in usb0 with name limelight.local
# - DHCP client in wlan0 with name limelight....
# - DHCP client in eth0 with name limelight....
# -------------------------------------------------------
# Nadège LEMPERIERE, @30th April 2025
# Latest revision: 30th April 2025
# -------------------------------------------------------


# 0 - Retrieve absolute path to this script
script=$(readlink -f $0)
scriptpath=`dirname $script`

# 1 - Configure addresses for eth0 and usb0 interfaces
echo ""
echo "❶ Configuring usb0 and eth0 ip range"

source $scriptpath/../conf/env
export ADDRESS_SCRIPT_PATH=/usr/local/bin/limelight-address.sh

envsubst '$ETH_IP_GATEWAY,$USB_IP_GATEWAY_LINUX,$USB_IP_GATEWAY_WINDOWS' < $scriptpath/../data/limelight-address.sh > $ADDRESS_SCRIPT_PATH
chmod +x $ADDRESS_SCRIPT_PATH

echo "  ➡️  Created limelight address script"

SERVICE_PATH=/etc/systemd/system/limelight-address.service
envsubst '$ADDRESS_SCRIPT_PATH' < $scriptpath/../data/limelight-address.service > $SERVICE_PATH

echo "  ➡️  Prepared limelight address service"

# Check if service already exists
if systemctl list-unit-files | grep -q limelight-address.service; then
    echo "  🔁 Service already exists. Reloading, enabling, and restarting."
    systemctl daemon-reload
    systemctl enable limelight-address.service
    systemctl restart limelight-address.service
else
    echo "  🆕 Installing new service."
    systemctl daemon-reload
    systemctl enable limelight-address.service
    systemctl start limelight-address.service
fi

if ! systemctl is-active --quiet limelight-address.service; then
    echo "  ❌ Failed to start limelight address service"
    exit 1
fi

echo "✅ Limelight ip range configuration complete"

# 2 - Configure DHCP servers for both usb0 and eth0
echo ""
echo "❷ Configuring DHCP servers on usb0 and eth0"

shall_reboot=false
source $scriptpath/../conf/env

apt -qq update
apt -qq install -y dnsmasq
echo "  ➡️  Installed dnsmasq DHCP server "

# 2.1 - Create DHCP server for usb0 

envsubst '$USB_IP_ADDRESSES_LINUX' < $scriptpath/../data/usb0.conf > /etc/dnsmasq.d/usb0.conf
echo "  ➡️  Created DHCP configuration for usb0"

# 2.2 - Create DHCP server for usb1

envsubst '$USB_IP_ADDRESSES_WINDOWS' < $scriptpath/../data/usb1.conf > /etc/dnsmasq.d/usb1.conf
echo "  ➡️  Created DHCP configuration for usb1"

# 2.3 - Create DHCP server for eth0

envsubst '$ETH_IP_ADDRESSES,$ETH_IP_GATEWAY' < $scriptpath/../data/eth0.conf > /etc/dnsmasq.d/eth0.conf
echo "  ➡️  Created DHCP configuration for eth0"

systemctl restart dnsmasq

echo "  🔄 Restarted dnsmasq service"

echo "✅ DHCP servers ready."

# 3 - Publishing names for each interface
echo ""
echo "❸ Publishing names per interface"

# 3.1 - Limit avahi to wlan

#!/bin/bash
set -e

echo "🔧 Restricting Avahi to wlan0"

AVAHI_CONF="/etc/avahi/avahi-daemon.conf"

# Backup original config
if [ ! -f "${AVAHI_CONF}.bak" ]; then
    sudo cp "$AVAHI_CONF" "${AVAHI_CONF}.bak"
fi

# Edit avahi-daemon.conf
sudo sed -i \
    -e 's/^#*use-ipv4=.*/use-ipv4=yes/' \
    -e 's/^#*use-ipv6=.*/use-ipv6=no/' \
    "$AVAHI_CONF"

# Remove all allow-interfaces lines (even commented)
sed -i '/^[# ]*allow-interfaces=/d' "$AVAHI_CONF"

# Check if [server] section exists
if grep -q '^\[server\]' "$AVAHI_CONF"; then
    echo "✅ [server] section found, inserting allow-interfaces under it."

    # Insert allow-interfaces=usb0 under [server]
    sed -i '/^\[server\]/a allow-interfaces=usb0' "$AVAHI_CONF"
else
    echo "⚠️ No [server] section found, appending it at the end."

    # Add the section and setting at end
    echo "" >> "$AVAHI_CONF"
    echo "[server]" >> "$AVAHI_CONF"
    echo "allow-interfaces=usb0" >> "$AVAHI_CONF"
fi


# Restart Avahi
sudo systemctl restart avahi-daemon

echo "✅ Avahi now limited to wlan0 only."

# 3.2 - Install zeroconf based name resolver

apt -qq install -y python3-zeroconf

cp $scriptpath/../data/name_resolver.py /usr/local/bin/name_resolver.py

export DNS_SCRIPT_PATH=/usr/local/bin/limelight-dns.sh

envsubst '$ETH_IP_GATEWAY,$USB_IP_GATEWAY' < $scriptpath/../data/limelight-dns.sh > $DNS_SCRIPT_PATH
chmod +x $DNS_SCRIPT_PATH

echo "  ➡️  Created limelight dns script"

SERVICE_PATH=/etc/systemd/system/limelight-dns.service
envsubst '$DNS_SCRIPT_PATH' < $scriptpath/../data/limelight-dns.service > $SERVICE_PATH

echo "  ➡️  Prepared limelight dns service"

# Check if service already exists
if systemctl list-unit-files | grep -q limelight-dns.service; then
    echo "  🔁 Service already exists. Reloading, enabling, and restarting."
    systemctl daemon-reload
    systemctl enable limelight-dns.service
    systemctl restart limelight-dns.service
else
    echo "  🆕 Installing new service."
    systemctl daemon-reload
    systemctl enable limelight-dns.service
    systemctl start limelight-dns.service
fi

if ! systemctl is-active --quiet limelight-dns.service; then
    echo "  ❌ Failed to start limelight dns service"
    exit 1
fi

echo "✅ Limelight dns installation complete"

# 4 - Reboot to make sure everything is consistent
echo ""
echo "✅ All interfaces and hostnames available."
echo "🔄 Rebooting in 5 seconds... Press CTRL+C to cancel."
sleep 5
shutdown -r now