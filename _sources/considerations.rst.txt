Design considerations
=====================

Assumptions and Dependencies
----------------------------

Limelight supports Ethernet-only connectivity through `USB gadget`_.

.. _`USB gadget`: https://en.wikipedia.org/wiki/Ethernet_over_USB

General Constraints
-------------------

The Limelight 3A camera receives power via the FTC Control Hub’s USB-A 3.0 port. which is insufficient to power both the Raspberry Pi and the Limelight. 

Goals and Guidelines
--------------------

- Enable drop-in integration between Limelight 3A and Control Hub without modifying robot code or wiring.
- Ensure PI is accessible to the development laptop when the laptop is connected to the FTC dashboard over the control hub Wi-Fi.
- Provide reliable access to the PI for debugging during development.
- Support robust operation during hot-plugging of the Limelight or PI.
- Prioritize low-latency behavior for real-time testing and debugging.
- Require no configuration changes on the Control Hub or development laptop beyond existing Limelight requirements.

Development Methods and Contingencies
-------------------------------------

**LimeNurse** provides tests to check software installation on a laptop before integration with the FTC hub

Architectural Strategies
------------------------

Development Laptop Interface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

During tuning, the development laptop wireless connection is often limited to the control hub wifi to access FTC dashboard. Limelight services over raspberry pi must then use a wired connection.
The Raspberry Pi connects to the Control Hub via its USB-C port using USB gadget mode, emulating the Limelight interface. The remaining Ethernet port on the Pi is used to route Limelight traffic to the development laptop, which can then access the Limelight API.
This interface will provide SSH logging capabilities to access the Pi.

Control Hub Interface
~~~~~~~~~~~~~~~~~~~~~

**LimeNurse** uses USB gadget to provide Ethernet over USB with the same interface name as the Limelight. 
Since the Control Hub cannot power both devices, a USB splitter is used. Its data line connects to the Control Hub, while power is supplied independently using an official Raspberry Pi cable and a compatible power source (minimum 15W at 5V).
The USB splitter shall be carefully chosen to transport the 15W - 5A current. 

Limelight Interface
~~~~~~~~~~~~~~~~~~~

The PI power adaptor is not enough to power both PI and limelight. An USB splitter is used to supply additional power to the limelight. A standard USB splitter separating data from power is enough.
Limelight uses a USB C 3.0 port to connect to the Raspberry Pi.

Raspberry Pi software
~~~~~~~~~~~~~~~~~~~~~

Routing from limelight to Control Hub and developer laptop can not be performed using layer 2 bridging without preventing Pi SSH connection. iptables be used for unicast routing and custom components for broadcast UDP routing.

After a lot of trial and error with avahi default name management, which ended up providing name resolution for ping, ssh capabilities with a tuned command line, and failure in an http browser, raspberry pi uses its own name manager baed on python zeroconf.