
Architecture
============

Hardware Architecture
---------------------

Hardware architecture diagram
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following diagram gives the hardware architecture required to setup LimeNurse.

.. image:: images/hardware-architecture.png
   :alt: Hardware architecture
   :width: 800

Bill of materials
~~~~~~~~~~~~~~~~~

Trials and errors led to the following bill of materials, the list of parts on which **LimeNurse** has been successfully deployed.
Some other configurations may also be compatible, so each part has a justification of why it was chosen, so that users can consider other options with a discerning eye.

.. list-table:: Hardware components and references
   :widths: 20 20 50 10
   :header-rows: 1

   * - Name
     - Identification
     - Image
     - Justification
   * - `Raspberry Pi`_ 
     - SKU 784181
     - .. image:: images/pi5.png
          :width: 120
     - Supports USB gadget and provide an ethernet port on top of the USB C and USB A ones.
   * - `Mogood USB C Male to Dual USB C Female Cable`_ 
     - ASIN B0CB3M46Y5
     - .. image:: images/limelight-splitter.png
          :width: 120
     - Not critical - Provides limelight power from an external source
   * - `8086 USB C Data/Power Splitter`_ 
     - SKU 103677
     - .. image:: images/pi-splitter.png
          :width: 120
     - One of the few USB splitter handling the 15W / 5V power from Pi official power supply
   * - `Raspberry PI official power supply`_
     - SKU SC0623
     - .. image:: images/power.png
          :width: 120
     - Provide maximal power to Pi. Considered first to power both Pi and Limelight, but was not enough. Maybe not necessary for Pi alone
   * - `10" USB C - USB C cable`_
     - 
     - .. image:: images/cableCC.png
          :width: 120
     - Link the limelight on robot to the development stand while providing enough length for the robot to move
   * - `10" USB C - USB A cable`_
     - 
     - .. image:: images/cableCA.png
          :width: 120
     - Link the control hub on robot to the development stand while providing enough length for the robot to move

.. _`Raspberry Pi`: https://www.raspberrypi.com
.. _`Mogood USB C Male to Dual USB C Female Cable`: https://www.amazon.com/MOGOOD-Splitter-Adapter-Monitor-Charging/dp/B0CB3M46Y5/ref=asc_df_B0CB3M46Y5?mcid=cd76c850e7fc3868abd8b788f2979969&hvocijid=8809277218558578786-B0CB3M46Y5-&hvexpln=73&tag=hyprod-20&linkCode=df0&hvadid=721245378154&hvpos=&hvnetw=g&hvrand=8809277218558578786&hvpone=&hvptwo=&hvqmt=&hvdev=c&hvdvcmdl=&hvlocint=&hvlocphy=9004214&hvtargid=pla-2281435179098&th=1
.. _`8086 USB C Data/Power Splitter`: https://thepihut.com/products/usb-c-data-power-splitter
.. _`Raspberry PI official power supply`: https://www.raspberrypi.com/products/raspberry-pi-universal-power-supply/
.. _`10" USB C - USB C cable`: https://www.amazon.com/Durcord-Upgarded-Charging-Charger-Compatible/dp/B0CJHVS2ND?th=1
.. _`10" USB C - USB A cable`: https://www.amazon.com/Besgoods-Charger-Charging-Compatible-G7-2Pack/dp/B0B6F9DVZ3/ref=sr_1_1?crid=R2FS0C3SQ3PZ&dib=eyJ2IjoiMSJ9.D4dG9gukQqLuT6eezXZoL4X4fdRPpepyDNXhb3k-oD1pQphYd8ZElsUQ_vfgsEoMiBrsdtkIKDNxQTDjE7NVSZZtR2gqxVm1qPTF6di59jAuge7vmaEFF5TSZTpGpMO9eySv9ZVysH9KEE29dteXyW4UpH9cfhOMRdIQrTMLJ90hE6VM74kBORd348jd9ffCoI00FmnIuKiZvuTbxuASJ_9feBdoGNJS9hAdQY8xU3rsbBaewUJM0MQPCQGeiybA7xj0nLgP0Q3iRSC7HLs4lUBy4A9Qw35cu1yfMVvNaeY.scAzlwNV8u7s0l0RSEB6zRaFFNlPKD8Rs1oZRDFYfoM&dib_tag=se&keywords=besgoods%2Busb%2Bc%2Busb%2Ba%2Bgreen&qid=1746534171&s=electronics&sprefix=besgoods%2Busb%2Bc%2Busb%2Ba%2Bgreen%2Celectronics%2C60&sr=1-1&th=1


Internal Communications Architecture
------------------------------------


The following table shows the operational interfaces provided by **LimeNurse**

.. list-table:: Operational Interfaces Control Table
   :widths: 10 10 10 10 10 10 10 10 10 10 10
   :header-rows: 2

   * - Source
     - 
     -
     -
     - Connection
     - 
     - Destination
     - 
     - 
     -
     - Comments
   * - Component
     - Interface
     - Port
     - Name
     - Protocol
     - Data
     - Component
     - Interface
     - Port
     - Name
     -
   * - Developer laptop
     - Ethernet
     - 
     - 
     - udp
     - Name resolution exchanges
     - Raspberry PI
     - Ethernet (eth0)
     - 53, 67, 68, 5353
     - 
     - Avahi name resolution exchanges
   * - Developer laptop
     - Ethernet
     -
     -
     - http
     - limelight web client
     - Raspberry PI
     - Ethernet (eth0)
     - 5801
     - limelight.eth.local
     - Web client tuning and debug access
   * - Developer laptop
     - Ethernet
     -
     -
     - http + websockets
     - limelight video streams
     - Raspberry PI
     - Ethernet (eth0)
     - 5802, 5800, ...
     - limelight.eth.local
     - Video stream display
   * - Developer laptop
     - Ethernet
     - 
     - 
     - ssh
     - Pi commands
     - Raspberry PI
     - Ethernet (eth0)
     - 22
     - limelight.eth.local
     - Raspberry Pi debug access
   * - Control hub
     - USB A
     -
     -
     - http + websocket
     - limelight rest API requests and responses
     - Raspberry PI
     - USB C
     - 5807, 5806
     - limelight.local
     - Limelight vision result http access
   * - Raspberry Pi
     - USB C (eth1)
     -
     -
     - http
     - limelight web client
     - Limelight
     - USB C
     - 5801
     - limelight.local
     - Web client
   * - Raspberry Pi
     - USB C (eth1)
     -
     -
     - http + websockets
     - limelight video streams
     - Limelight
     - USB C
     - 5802, 5800, ...
     - limelight.local
     - Video stream display
   * - Raspberry Pi
     - USB C (eth1)
     -
     -
     - http + websocket
     - limelight rest API requests and responses
     - Raspberry PI
     - USB C
     - 5807, 5806
     - limelight.local
     - Limelight vision result http access


The following table shows the interfaces provided by **LimeNurse** for deployment testing purpose

.. list-table:: Test Interface Control Table
   :widths: 10 10 10 10 10 10 10 10 10 10 10
   :header-rows: 2

   * - Source
     - 
     -
     -
     - Connection
     - 
     - Destination
     - 
     - 
     -
     - Comments
   * - Component
     - Interface
     - Port
     - Name
     - Protocol
     - Data
     - Component
     - Interface
     - Port
     - Name
     -
   * - Developer laptop
     - USB A
     - 
     - 
     - udp
     - Name resolution exchanges
     - Raspberry PI
     - USB C (usb0)
     - 53, 67, 68, 5353
     - 
     - Avahi name resolution exchanges
   * - Developer laptop
     - Ethernet
     -
     -
     - http
     - limelight web client
     - Raspberry PI
     - USB C (usb0)
     - 5801
     - limelight.local
     - Web client tuning and debug access
   * - Developer laptop
     - USB A
     -
     -
     - http + websockets
     - limelight video streams
     - Raspberry PI
     - USB C (usb0)
     - 5802, 5800, ...
     - limelight.local
     - Video stream display
   * - Developer laptop
     - USB A
     -
     -
     - UDP
     - broadcast LLPhoneHome
     - Raspberry PI
     - USB C (usb0)
     - 5809
     - limelight.local
     - Limelight discovery
   * - Developer laptop
     - Ethernet
     -
     -
     - UDP
     - broadcast LLPhoneHome
     - Raspberry PI
     - Ethernet (eth0)
     - 5809
     - limelight.eth.local
     - Limelight discovery
   * - Developer laptop
     - USB A
     -
     -
     - http + websocket
     - limelight rest API requests and responses
     - Raspberry PI
     - USB C (usb0)
     - 5807, 5806
     - limelight.local
     - Limelight vision result http access
   * - Developer laptop
     - Ethernet
     -
     -
     - http + websocket
     - limelight rest API requests and responses
     - Raspberry PI
     - Ethernet (eth0)
     - 5807, 5806
     - limelight.eth.local
     - Limelight vision result http access

Software Architecture
---------------------

**LimeNurse** relies on standard linux services. It uses systemd services to ensure robustness and persistence of the deployment

.. image:: images/software-architecture.png
   :alt: Software architecture
   :width: 800


Data Link Layer (2) configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

USB gadget drivers are activated in the Pi OS to enable ethernet over USB on usb0. 
This is a once shot firmware configuration, persisted by the firmware persistence mechanisms. 

Then the USB descriptors are configurated to mock the limelight ones and make it discoverable by the Control Hub. 
Descriptors setting is managed by a systemd service restarted on Pi start.

Network Layer (3) configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

IP management services is deployed on both ethernet and USB interfaces. 
Ethernet and USB gateways are assigned fixed IP. IP setting is managed by a systemd service restarted on Pi start.
Ethernet and USB interfaces expose a DHCP service to provide communcations with development laptop and control hub through an IP in their hosted networks.
This is a once shot dnsmasq service configuration, persisted by the dnsmasq persistence mechanisms.

Gateways are assigned names. 
This is managed by a zeroconf based python script.
The python script regularly update the dns services to make sure the name keep being resolved.
The resolver script is managed by a systemd service restarted on Pi start.

Transport Layer (4) configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

UDP and TCP unicast forwarding between interfaces are managed using firewall rules. Port 22 on eth 0 is not forwarded to provide ssh services
The rules setting script is managed by a systemd service restarted on Pi start.

UDP messages are broadcasted to enable limelight discovery. 
They are not forwarded by iptables and are then managed by a custom Python script.
The python script is robust to interface loss through limelight disconnection.
It monitors interface and restore connection and transfer once the interface is back.
The forwarder script is managed by a systemd service restarted on Pi start.