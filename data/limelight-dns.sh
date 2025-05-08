#!/bin/bash
set -e

# Configure name resolution

echo ""
echo "Launch name resolver"
python3 /usr/local/bin/name_resolver.py --usb limelight.local  --eth limelight.eth.local --wlan $(hostname).local > /var/log/name_forwarder.log 2>&1 &  # usb0

echo ""
echo "🎉 Limelight dns setup complete!"
echo "✅ Limelight dns ready!"