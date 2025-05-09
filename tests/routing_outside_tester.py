# -------------------------------------------------------
# Copyright (c) [2025] Nadege Lemperiere
# All rights reserved
# -------------------------------------------------------
"""
Test limelight gadget configuration from the user point
of view
"""
# -------------------------------------------------------
# Nadège LEMPERIERE, @30th April 2025
# Latest revision: 30th April 2025
# -------------------------------------------------------

from logging                        import getLogger
from os                             import path
from re                             import search
from http                           import client

# Limelight includes
from limelight                      import discover_limelights, Limelight

# Logger configuration settings
logg_conf_path = path.normpath(path.join(path.dirname(__file__), '../conf/logging.conf'))
env_path = path.normpath(path.join(path.dirname(__file__), '../conf/env'))
limelight_descriptors_path = path.normpath(path.join(path.dirname(__file__), '../data/limelight-gadget.json'))

class RoutingOutsideTester:
    """ 
    Class for testing Limelight gadget accessibility from the user's machine 
    over both USB and Ethernet interfaces. It performs checks using HTTP, 
    REST API, and NetworkTables protocols to validate device presence and 
    behavior on both interfaces.
    """

    sLimelightVendor = "1d6b"
    sLimelightProduct = "0104"

    #pylint: disable=R0913, C0301
    def __init__(self):
        """ Constructor """

        # Initialize logger
        self.__logger = getLogger('outside')
        self.__logger.info('INITIALIZING OUTSIDE GADGET TEST')

        self.__is_ready = False

    def configure(self, platform) :
        """
        Load the reference USB and Ethernet IPs from the environment configuration file.
        Marks the tester as ready if both IPs are found.
        """

        self.__logger.info('CONFIGURING OUTSIDE GADGET TEST')

        self.__is_ready = False

        self.__reference_eth_ip = ""
        with open(env_path, 'r') as file:
            match = search(r'ETH_IP_GATEWAY=([\d\.]+)', file.read())
            if match : 
                self.__reference_eth_ip = match.group(1)

        # Read the USB gateway IP address from the environment file
        usb_linux_ip = ""
        with open(env_path, 'r') as file:
            match = search(r'USB_IP_GATEWAY_LINUX=([\d\.]+)', file.read())
            if match : 
                usb_linux_ip = match.group(1)

        # Read the USB gateway IP address from the environment file
        usb_windows_ip = ""
        with open(env_path, 'r') as file:
            match = search(r'USB_IP_GATEWAY_WINDOWS=([\d\.]+)', file.read())
            if match : 
                usb_windows_ip= match.group(1)
        
        self.__shall_test_names = True
        
        if(platform == 'windows') : 
            self.__shall_test_names = False
            self.__reference_usb_ip = usb_windows_ip
        elif (platform == 'linux') : 
            self.__shall_test_names = True
            self.__reference_usb_ip = usb_linux_ip
        elif (platform == 'ios') : 
            self.__shall_test_names = True
            self.__reference_usb_ip = usb_linux_ip
        else :
            self.__logger.error("Unknown platform " + platform + " shall be windows ,linux or ios")

        # Set readiness to True only if both IP addresses are found
        if len(self.__reference_eth_ip) != 0 and len(self.__reference_usb_ip) != 0:
            self.__is_ready = True


    def run(self) :
        """
        Execute all outside tests if the configuration is complete.
        Currently enabled: NetworkTables access test.
        Returns True if all tests pass, otherwise False.
        """

        result = False

        if self.__is_ready : 

            self.__logger.info('RUNNING OUTSIDE TESTS')
            result = True

            rest_api_check = self.__check_rest_api()
            print(rest_api_check)
            if not rest_api_check : result = False

            webclient_check = self.__check_client()
            if not webclient_check : result = False

        return result

    def __check_client(self) :
        """
        Attempt to connect to the Limelight web client interface on port 5801
        for both USB and Ethernet IPs and ensure the response is HTTP 200 OK.
        """

        result = True
        for ip in [self.__reference_eth_ip, self.__reference_usb_ip]:
            try:
                conn = client.HTTPConnection(ip, 5801, timeout=2)
                conn.request("GET", "/")
                response = conn.getresponse()
                if response.status != 200:
                    self.__logger.error(f"HTTP client on {ip}:5801 returned status {response.status}")
                    result = False
                else:
                    self.__logger.info(f"HTTP client on {ip}:5801 is reachable")
                conn.close()
            except Exception as e:
                self.__logger.error(f"HTTP client access failed on {ip}:5801 with error: {e}")
                result = False

        if self.__shall_test_names :
            for name in ["limelight.eth.local", "limelight.local"]:
                try:
                    conn = client.HTTPConnection(name, 5801, timeout=2)
                    conn.request("GET", "/")
                    response = conn.getresponse()
                    if response.status != 200:
                        self.__logger.error(f"HTTP client on {name}:5801 returned status {response.status}")
                        result = False
                    else:
                        self.__logger.info(f"HTTP client on {name}:5801 is reachable")
                    conn.close()
                except Exception as e:
                    self.__logger.error(f"HTTP client access failed on {name}:5801 with error: {e}")
                    result = False

        return result

    def __check_rest_api(self) : 
        """
        Use the Limelight discovery and REST API to validate correct responses
        from both USB and Ethernet interfaces, including metadata like name and FPS.
        """
            
        result = True 

        limelights = []
        ips = discover_limelights(debug=True)
        for ip in ips :
            if ip not in limelights :
                limelights.append(ip)

        if len(limelights) != 2 :
            self.__logger.error('--> Found ' + str(len(limelights)) + ' limelight interfaces instead of 2')
            result = False
        if self.__reference_eth_ip not in limelights :
            self.__logger.error('--> Ethernet interface for limelight not found')
            result = False
        if self.__reference_usb_ip not in limelights :
            self.__logger.error('--> USB gadget interface for limelight not found')
            result = False

        if result :
            self.__logger.info("Ethernet and USB gadget interfaces found for limelight")

            eth = Limelight(self.__reference_eth_ip)
            usb = Limelight(self.__reference_usb_ip)

            eth_status = eth.get_status()
            usb_status = usb.get_status()

            if 'name' not in eth_status : 
                self.__logger.error('Missing name in ethernet status')
                result = False
            if 'name' not in usb_status : 
                self.__logger.error('Missing name in usb status')
                result = False
            if eth_status['name'] != 'limelight' :
                self.__logger.error('Ethernet name is ' + eth_status['name'] + ' instead of limelight')
                result = False
            else :
                self.__logger.info('Ethernet name is ' + eth_status['name'] )
            if usb_status['name'] != 'limelight' :
                self.__logger.error('USB gadget name is ' + usb_status['name'] + ' instead of limelight')
                result = False
            else :
                self.__logger.info('USB gadget name is ' + usb_status['name'] )

            if 'fps' not in eth_status : 
                self.__logger.error('Missing fps in ethernet status')
                result = False
            if 'fps' not in usb_status : 
                self.__logger.error('Missing fps in usb status')
                result = False
            if eth_status['fps'] <= 0 :
                self.__logger.error('Ethernet fps is ' +  str(eth_status['fps']))
                result = False
            else :
                self.__logger.info('Ethernet name fps is ' + str(eth_status['fps']))
            if usb_status['fps'] <= 0 :
                self.__logger.error('USB gadget fps is ' + str(usb_status['fps']))
                result = False
            else :
                self.__logger.info('USB gadget fps is ' + str(usb_status['fps']))
            

        return result