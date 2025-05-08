#! /bin/bash
# -------------------------------------------------------
# Copyright (c) [2025] Nadege Lemperiere
# All rights reserved
# -------------------------------------------------------
# Configure a raspberry pi usb gadget to behave as a 
# limelight. Script shall be launched right after the
# Pi OS has been installed
# -------------------------------------------------------
# Nadège LEMPERIERE, @29th April 2025
# Latest revision: 29th April 2025
# -------------------------------------------------------


# 0 - Retrieve absolute path to this script
script=$(readlink -f $0)
scriptpath=`dirname $script`

# 1 - Configure Raspberry Pi usb gadget mode
echo ""
echo "❶ Activating Raspberry PI usb gadget mode"

shall_reboot=false

# 1.1 - Update cmdline.txt
CMDLINE_FILE="/boot/firmware/cmdline.txt"
cp "$CMDLINE_FILE" "${CMDLINE_FILE}.bak"
if ! grep -q 'modules-load=dwc2' "$CMDLINE_FILE"; then
    sed -i 's/\brootwait\b/& modules-load=dwc2/' "$CMDLINE_FILE"
    echo "  ➡️  modules-load=dwc2 added."
    shall_reboot=true
else
    echo "  *️⃣  modules-load=dwc2 already present, skipping."
fi

if ! grep -q 'modules-load=dwc2' "$CMDLINE_FILE"; then
    echo "  ❌  Failed in modifying $CMDLINE_FILE"
    exit 1
else 
    echo "  ➡️  Successfully modified $CMDLINE_FILE"
fi

CONFIG_FILE="/boot/firmware/config.txt"
cp "$CONFIG_FILE" "${CONFIG_FILE}.bak"

# 1.2 - Ensure otg_mode=1 is present and uncommented
if grep -q '^[[:space:]]*#.*otg_mode=1' "$CONFIG_FILE"; then
    # Uncomment it if it's commented
    sed -i 's/^[[:space:]]*#\s*\(otg_mode=1\)/\1/' "$CONFIG_FILE"
    echo "  ➡️  Uncommented existing otg_mode=1 line."
    shall_reboot=true
elif ! grep -q '^[[:space:]]*otg_mode=1' "$CONFIG_FILE"; then
    # Append if it's missing completely
    echo "otg_mode=1" >> "$CONFIG_FILE"
    echo "  ➡️  Added missing otg_mode=1 at end of file."
    shall_reboot=true
else
    echo "  *️⃣  otg_mode=1 already present and uncommented."
fi

# 1.3 - Ensure dtoverlay=dwc2 after [all]
if grep -q '^\[all\]' "$CONFIG_FILE"; then
    # Insert dtoverlay=dwc2 immediately after [all] if not already present
    if ! grep -A1 '^\[all\]' "$CONFIG_FILE" | grep -q 'dtoverlay=dwc2'; then
        # Use awk to insert line safely after [all]
        awk '/^\[all\]/{print; print "dtoverlay=dwc2"; next}1' "$CONFIG_FILE" > "${CONFIG_FILE}.tmp" && mv "${CONFIG_FILE}.tmp" "$CONFIG_FILE"
        echo "  ➡️  Inserted dtoverlay=dwc2 after [all]."
        shall_reboot=true
    else
        echo "  *️⃣  dtoverlay=dwc2 already present after [all]."
    fi
else
    echo "  ‼️  Warning: No [all] section found in $CONFIG_FILE!"
    # Optionally add [all] + dtoverlay if critical
    echo -e "\n[all]\ndtoverlay=dwc2" >> "$CONFIG_FILE"
    echo "  ➡️  Added missing [all] section and dtoverlay=dwc2."
    shall_reboot=true
fi

if ! grep -A1 '^\[all\]' "$CONFIG_FILE" | grep -q 'dtoverlay=dwc2'; then
    echo "  ❌  Failed in modifying $CONFIG_FILE"
    exit 1
elif ! grep -q '^[[:space:]]*otg_mode=1' "$CONFIG_FILE"; then
    echo "  ❌  Failed in modifying $CONFIG_FILE"
    exit 1
else 
    echo "  ➡️  Successfully modified $CONFIG_FILE"
fi

# 1.4 - Reboot if needed
if [ "$shall_reboot" = true ] ; then
    echo "✅  USB gagdet activated. Reboot the system to apply changes and rerun the script."
    echo "🔄  Rebooting in 5 seconds... Press CTRL+C to cancel."
    sleep 5
    shutdown -r now
fi

# 2 - Mock limelight descriptors
echo ""
echo "❷ Mocking limelight usg gadget descriptors"

# 2.1 - Install limelight gadget service
source $scriptpath/../conf/env
export GADGET_SCRIPT_PATH=/usr/local/bin/limelight-gadget.sh

envsubst '$USB_IP_GATEWAY' < $scriptpath/../data/limelight-gadget.sh > $GADGET_SCRIPT_PATH
chmod +x $GADGET_SCRIPT_PATH

echo "  ➡️  Created limelight gadget script"

envsubst '$GADGET_SCRIPT_PATH' < $scriptpath/../data/limelight-gadget.service > /etc/systemd/system/limelight-gadget.service

echo "  ➡️  Created limelight gadget service"

# 2.2 - Reload service
systemctl daemon-reload
echo "  🔄 Reloaded systemd daemon"

systemctl enable limelight-gadget.service
systemctl start limelight-gadget.service

if ! systemctl is-active --quiet limelight-gadget.service; then
    echo "  ❌ Failed to start limelight gadget service"
    exit 1
fi

echo "✅  Limelight USB Gadget installation complete"

# 4 - Reboot to make sure everything is consistent
echo ""
echo "🎉 Limelight USB Gadget installation complete!"
echo "✅ Limelight USB Gadget ready"
echo "🔄 Rebooting in 5 seconds... Press CTRL+C to cancel."
sleep 5
shutdown -r now