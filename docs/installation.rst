
Installation
============

Prerequisites
-------------

The Raspberry Pi shall have been initialized with a basic OS.

- Download and install the **Raspberry Pi Imager** on your laptop.
- Insert the Micro SD card into your laptop.
- Launch Raspberry Pi Imager:
   - Device: **Raspberry Pi 5**
   - Operating System: **Raspberry Pi OS (64-bit)**
   - Storage: Your Micro SD card
- Customize OS settings:
   - Hostname : **limenurse.local**
   - Set username, password
   - Configure Wi-Fi and locale
   - Enable SSH through password
- Flash the card and verify.

**limenurse.local** is the name to use to access the PI through wifi. 
Any other name can be used, as long as it's not limelight.local which we will use later on on the USB interface.
The installation script will adapt to the chosen name by readiing hostname from the PI installation

Insert the Micro SD card into the Raspberry Pi 5, connect to the Pi through your wifi.

Configuration
-------------

- Clone this repository locally 
- Setup the target gateway IP addresses for the pi usb0 and eth0 interfaces in conf/env.

Here is an example of the env file to modify if needed

.. literalinclude:: ../conf/env

IP address should be something like 172.XXX.0.1 with XXX not being 29 to avoid IP conflict with the real limelight inside the Pi.

Data Link Layer Deployment
--------------------------

This first step will configure the PI to provide limelight like USB gadget services on its usb0 interface. 
It's performed by a bash script which will reboot the PI once and has to be relaunched to finalize the USB gadget configuration 

.. code-block:: bash 

  sudo scripts/01-configure-gadget.sh  

- Enable USB device mode in the Raspberry Pi firmware
- Load necessary kernel modules (dwc2)
- Set device-tree overlays
- Install the `limelight-gadget.sh`_ script to mock limelight USB descriptors and force usb0 gateway IP address
- Install the systemd `limelight-gadget.service`_ to start and persist the script

.. _`scripts/01-configure-gadget.sh`: ../scripts/01-configure-gadget.sh
.. _`limelight-gadget.sh`: ../data/limelight-gadget.sh
.. _`limelight-gadget.service`: ../data/limelight-gadget.service

Network Layer Deployment
------------------------

The second step is to deploy network management services on both eth0 and usb0

.. code-block:: bash 
  
  sudo scripts/02-configure-network.sh  

- Configure dnsmasq to offer DHCP services on both interfaces and allow laptop to communicate sith those interfaces by getting an IP address on thei network
- Restrict the current Pi name mangement system to the wifi wlan0 interface
- Publish limelight.local name on usb0 gateway and limelight.eth.local on eth0 gateway

.. _`scripts/02-configure-network.sh`: scripts/02-configure-network.sh

After the reboot, the PI is accessible from wifi, ethernet and usb gadget interfaces with different names :

- The wifi wlan0 interface keeps the name configured at Pi installation : **limenurse.local**
- The ethernet eth0 interface gets **limelight.eth.local** name 
- The USB gadget usb0 interface gets **limelight.local** name to fully mock the PI

ssh login from development laptop through eth0 interface shall now be done using

.. code-block:: bash
  
  ssh -o ConnectTimeout=5 user@limelight.eth.local

This command line makes sure the dns request accepts IPv4 answer and does not wait indefinitely to an IPv6 answer.

Transport Layer Deployment
--------------------------

The thirs step is to launch forward data between interfaces

.. code-block:: bash 
  
  sudo scripts/03-configure-routing.sh  

- Install the `udp_forwarder.py`_ script to manage udp broadcast network data
- Install the `limelight-routing.sh`_ script to configure iptables for unicast data transfer between interfaces and udp_forwarder start
- Install the systemd `limelight-routing.service`_ to start and persist the script

.. _`scripts/03-configure-routing.sh`: scripts/03-configure-ethernet.sh
.. _`limelight-routing.sh`: ../data/limelight-routing.sh
.. _`limelight-routing.service`: ../data/limelight-routing.service
.. _`udp_forwarder.py`: ../data/udp_forwarder.py

