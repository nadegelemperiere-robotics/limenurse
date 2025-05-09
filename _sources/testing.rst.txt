
Testing
=======

Each installation step comes with its set of tests to make sure **LimeNurse** works as expected

Ouside tests
------------

Those tests shall be performed on the development laptop, or any laptop enabling connection of the Raspberry Pi on USB C and ethernet interfaces.
iOs and linux laptop shall have lsusb installed and sudo access. 
Windows computer shall have usbview installed and in the path. It will also require enabling scripts on powershell

The first step shall be launched after the Data Link Layer deployment has been performed

.. code-block ::

    # Linux
    scripts/01-configure-gadget-test.sh --source outside --platform <ios/linux>
    # Windows
    scripts/01-configure-gadget-test.ps1 --source outside --platform windows # Windows

- Look for an USB device matching limelight vendor and product
- Gather its USB descriptors using lsusb
- Compare them to real limelight ones

PS : If the tests are not performed on a Linux laptop (or linux VM), the usb descriptors won't be precise enough for the test to succeed.

The second step shall be launched after the Network Layer deployment has been performed
For the following tests, the pi needs to be connected to the test laptop both through USB and ethernet.

.. code-block ::

    # Linux
    scripts/02-configure-network-test.sh --source outside --platform <ios/linux> --user <ssh user> --password <ssh password> --hostname limenurse
    # Windows
    scripts/02-configure-network-test.ps1 --source outside --platform windows --user <ssh user> --password <ssh password> --hostname limenurse

- Check that limelight.local and limelight.eth.local names resolve to the configured IP (except for Windows)
- Check that limenurse.local resolve to an IP (depending on the wifi router on which Pi is connected to wifi)
- Check that the ethernet, USB and wlan IP are pingable
- Check that limenurse.local is pingable 
- Check that limelight.local, limelight.eth.local are pingable (except for Windows)
- Check that ssh connection on Pi is possible through ethernet and wlan IP
- Check that ssh connection on Pi is possible through limenurse.local
- Check that ssh connection on Pi is possible through limelight.eth.local (except for Windows)

The third step shall be launched after the Transport Layer deployment has been performed
For the following tests, the limelight needs to be connected to the raspberry pi.

.. code-block ::

    # Linux / iOs
    scripts/04-configure-routing-test.sh --source outside --platform <ios/linux>
    # Windows
    scripts/04-configure-routing-test.ps1 --source outside --platform windows

- Check that the PI is discoverable as a limelight on both ethernet and USB interfaces using python limelightlib
- Check that the limelight Rest API is accessible on both ethernet and USB interfaces using python limelightlib
- Check that the limelight webclient is accessible on both ethernet and USB interfaces


Inside tests
------------

Those tests shall be performed on the Pi.

The first step shall be launched after the Data Link deployment has been done

.. code-block ::

    scripts/01-configure-gadget-test.sh --source inside

- Check that configfs has been mounted
- Check that libcomposite module has been installed
- Check that descriptors files exists
- Check that gadget has been bind to UDC drivers
- Check that `limelight-gadget.service`_ is enabled and active
- Check that the usb0 interface has the configured ip address

.. _`limelight-gadget.service`: ../data/limelight-gadget.service


The second step shall be launched after the Network deployment has been performed

.. code-block ::

    scripts/02-configure-network-test.sh --source inside --user <ssh user> --password <ssh password> --hostname limenurse

- Check that `limelight-address.service`_ is enabled and active
- Check that the eth0 and usb0 interfaces have the required ip address
- Check that dnsmasq service is enabled and active
- Check that `limelight-dns.service`_ is enabled and active
- Check that avahi-daemon is enabled and active
- Check that python resolver runs
- Check that the resolver log file exist and does not contain errors


The third step shall be launched after the Transport Layer deployment has been performed

.. code-block ::

    scripts/03-configure-routing-test.sh --source inside

- Check that `limelight-routing.service`_ is enabled and active
- Check that python forwarder runs
- Check that the forwarder log file exist and does not contain errors

.. _`limelight-routing.service`: ../data/limelight-routing.service
