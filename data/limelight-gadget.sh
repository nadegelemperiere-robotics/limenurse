#!/bin/bash
set -e

# -----------------------------------------------------
# Ensure configfs is mounted
# -----------------------------------------------------

echo ""
echo "❶ Mounting configfs"

if ! mountpoint -q /sys/kernel/config; then
    mount -t configfs none /sys/kernel/config
    echo "  ➡️ configfs mounted"
else
    echo "  *️⃣ configfs already mounted."
fi
modprobe libcomposite

echo "  ✅ configfs is ready."

# -----------------------------------------------------
# Cleaning and creating limelight gadget folder
# -----------------------------------------------------

echo ""
echo "❷ Creating limelight gadget folder"
GADGET_DIR=/sys/kernel/config/usb_gadget/

# Remove old gadget if exists
if [ -d "$GADGET_DIR/limelight" ]; then
    echo "  🧹 Cleaning up old gadget"
    cd $GADGET_DIR/limelight
    echo "" > UDC || true
    sleep 1
    cd $GADGET_DIR
    rm -rf limelight || true
    sleep 1

    if [ ! -d "$GADGET_DIR/limelight" ]; then
        echo "  ➡️ $GADGET_DIR/limelight folder no longer exists"
    else
        echo "  ❌ $GADGET_DIR/limelight was not removed"
        exit 1
    fi
fi

echo "  🛠 Creating Limelight USB gadget..."

mkdir -p $GADGET_DIR/limelight

if [ -d "$GADGET_DIR/limelight" ]; then
    echo "  ➡️ $GADGET_DIR/limelight created"
else
    echo "  ❌ $GADGET_DIR/limelight not created"
    exit 1
fi

echo "  ✅ limelight folder is ready."

# -----------------------------------------------------
# Mocking limelight descriptors
# -----------------------------------------------------

echo ""
echo "❸ Creating descriptors"


cd $GADGET_DIR/limelight

echo "0x1d6b" > idVendor
echo "0x0104" > idProduct
echo "0x02" > bDeviceClass
echo "0x00" > bDeviceSubClass
echo "0x00" > bDeviceProtocol
echo "0x4000" > bcdDevice
echo "0x0200" > bcdUSB
echo "64" > bMaxPacketSize0

mkdir -p strings/0x409
echo "100000006cf90866" > strings/0x409/serialnumber
echo "Limelight" > strings/0x409/manufacturer
echo "Raspberry Pi Compute Module 4 Rev 1.1" > strings/0x409/product

# Create Microsoft OS Descriptors (for RNDIS discovery)
mkdir -p os_desc
echo "1" > os_desc/use
echo "0xcd" > os_desc/b_vendor_code
echo "MSFT100" > os_desc/qw_sign

# Configuration 1 - ECM
mkdir -p configs/c.1
mkdir -p configs/c.1/strings/0x409
echo "CDC" > configs/c.1/strings/0x409/configuration
echo 250 > configs/c.1/MaxPower
echo 0xc0 > configs/c.1/bmAttributes

mkdir -p functions/ecm.usb0
echo "00:1A:2C:F9:08:66" > functions/ecm.usb0/dev_addr
echo "00:1A:2C:F9:08:67" > functions/ecm.usb0/host_addr

ln -s functions/ecm.usb0 configs/c.1/

# Configuration 2 - RNDIS
mkdir -p configs/c.2
mkdir -p configs/c.2/strings/0x409
echo "RNDIS" > configs/c.2/strings/0x409/configuration
echo 250 > configs/c.2/MaxPower
echo 0xc0 > configs/c.2/bmAttributes

mkdir -p functions/rndis.usb0
echo "00:1A:2E:F9:08:67" > functions/rndis.usb0/dev_addr
echo "00:1A:2E:F9:08:66" > functions/rndis.usb0/host_addr
mkdir -p functions/rndis.usb0/os_desc/interface.rndis
echo "RNDIS" > functions/rndis.usb0/os_desc/interface.rndis/compatible_id
echo "5162001" > functions/rndis.usb0/os_desc/interface.rndis/sub_compatible_id

ln -s functions/rndis.usb0 configs/c.2/

# Link os_desc to RNDIS config after all configs/functions are in place
ln -s configs/c.2 os_desc

echo "  ✅ limelight descriptors created."

# -----------------------------------------------------
# Binding to UDC
# -----------------------------------------------------
echo ""
echo "❹ Binding to UDC for enumeration"

# Final binding — after all configs, functions, descriptors ready
if [ -e UDC ]; then
    UDC_NAME=$(ls /sys/class/udc | head -n 1)
    echo "  🛠 Binding to UDC: $UDC_NAME..."
    echo "$UDC_NAME" > UDC
else
    echo "  ❌ UDC file not found, cannot bind gadget!"
    exit 1
fi

echo ""
echo "🎉 Limelight USB Gadget setup complete!"
echo "✅ Limelight USB Gadget ready!"