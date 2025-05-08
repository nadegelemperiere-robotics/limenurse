#!/bin/bash
set -e

# Configure DHCP servers for both usb0 and eth0
echo ""
echo "Configuring eth0 and usb0 fixed IP"

# Wait for usb0 to appear (max 10 seconds)
for i in {1..10}; do
    if ip link show usb0 > /dev/null 2>&1; then
        break
    fi
    echo "  ⏳ Waiting for usb0 to appear ($i/10)..."
    sleep 1
done

if ip link show usb0 > /dev/null 2>&1; then
    echo "  🔧 Setting static IP for usb0..."
    ip addr flush dev usb0 || true
    ip -6 addr flush dev usb0 scope global || true
    ip addr add $USB_IP_GATEWAY_LINUX/24 dev usb0
    ip link set usb0 up
    echo "  ➡️  usb0 interface got IP $USB_IP_GATEWAY_LINUX"
else
    echo "  ❌ usb0 interface not found, skipping IP configuration!"
fi


# Wait for usb1 to appear (max 10 seconds)
for i in {1..10}; do
    if ip link show usb1 > /dev/null 2>&1; then
        break
    fi
    echo "  ⏳ Waiting for usb1 to appear ($i/10)..."
    sleep 1
done

if ip link show usb1 > /dev/null 2>&1; then
    echo "  🔧 Setting static IP for usb1..."
    ip addr flush dev usb0 || true
    ip -6 addr flush dev usb0 scope global || true
    ip addr add $USB_IP_GATEWAY_WINDOWS/24 dev usb1
    ip link set usb1 up
    echo "  ➡️  usb1 interface got IP $USB_IP_GATEWAY_WINDOWS"
else
    echo "  ❌ usb1 interface not found, skipping IP configuration!"
fi

# Wait for eth0 to appear (max 10 seconds)
for i in {1..10}; do
    if ip link show eth0 > /dev/null 2>&1; then
        break
    fi
    echo "  ⏳ Waiting for eth0 to appear ($i/10)..."
    sleep 1
done

if ip link show eth0 > /dev/null 2>&1; then
    echo "  🔧 Setting static IP for eth0..."
    ip addr flush dev eth0 || true
    ip -6 addr flush dev eth0 scope global || true
    ip addr add $ETH_IP_GATEWAY/24 dev eth0
    ip link set eth0 up

    echo "  ➡️  eth interface got IP $ETH_IP_GATEWAY"
else
    echo "  ❌ eth0 interface not found, skipping IP configuration!"
fi

echo ""
echo "🎉 Limelight network setup complete!"
echo "✅ Limelight network ready!"