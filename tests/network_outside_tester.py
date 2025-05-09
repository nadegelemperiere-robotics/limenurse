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

# System includes
from logging                        import getLogger
from os                             import path
from subprocess                     import run, DEVNULL, PIPE
from re                             import search
from platform                       import system
from socket                         import gethostbyname, AF_INET

# Logger configuration settings
logg_conf_path = path.normpath(path.join(path.dirname(__file__), '../conf/logging.conf'))
env_path = path.normpath(path.join(path.dirname(__file__), '../conf/env'))
limelight_descriptors_path = path.normpath(path.join(path.dirname(__file__), '../data/limelight-gadget.json'))

class NetworkOutsideTester:
    """ 
    Class to perform network validation from an external host's perspective. 
    It verifies hostname resolution, ping accessibility, and SSH login capability 
    for a Limelight gadget connected via USB, Ethernet, and Wi-Fi.
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

    def configure(self, platform, user, hostname, password) :
        """Configure the tester.

        Args:
            platform (str): OS on which outside tests are executed (windows, ios, linux)
            user (str): SSH username (used only for outside tests).
            hostname (str): Hostname or IP address of the remote machine (used only for outside tests).
            password (str): SSH password (used only for outside tests).
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
        self.__shall_use_sshpass = True
        
        if(platform == 'windows') : 
            self.__shall_test_names = False
            self.__shall_use_sshpass = False
            self.__reference_usb_ip = usb_windows_ip
        elif (platform == 'linux') : 
            self.__shall_test_names = True
            self.__shall_use_sshpass = True
            self.__reference_usb_ip = usb_linux_ip
        elif (platform == 'ios') : 
            self.__shall_test_names = True
            self.__shall_use_sshpass = True
            self.__reference_usb_ip = usb_linux_ip
        else :
            self.__logger.error("Unknown platform " + platform + " shall be windows ,linux or ios")

        self.__user = user
        self.__hostname = hostname
        self.__password = password

         # Set readiness to True only if both IP addresses are found
        if len(self.__reference_eth_ip) != 0 and len(self.__reference_usb_ip) != 0 :
            self.__is_ready = True


    def run(self) :

        result = False

        if self.__is_ready : 

            self.__logger.info('RUNNING OUTSIDE TESTS')
            result = True

            if self.__shall_test_names : 
                usb_ip = NetworkOutsideTester.resolve("limelight.local")
                if usb_ip == self.__reference_usb_ip :
                    self.__logger.info('--> USB gadget name is correctly resolved to ip ' + self.__reference_usb_ip)
                elif len(usb_ip) != 0:
                    self.__logger.error('--> USB gadget name is resolved to ip %s instead of %s', usb_ip, self.__reference_usb_ip)
                else :
                    self.__logger.error('--> USB gadget name is not resolved')

            if self.__shall_test_names : 
                eth_ip = NetworkOutsideTester.resolve("limelight.eth.local")
                if eth_ip == self.__reference_eth_ip :
                    self.__logger.info('--> Ethernet name is correctly resolved to ip ' + self.__reference_eth_ip)
                elif len(eth_ip) != 0 :
                    self.__logger.error('--> Ethernet name is resolved to ip %s instead of %s', eth_ip, self.__reference_eth_ip)
                else :
                    self.__logger.error('--> Ethernet name is not resolved')

            wlan_ip = NetworkOutsideTester.resolve(self.__hostname + ".local")
            if len(wlan_ip) != 0 :
                self.__logger.info('--> Wlan name is resolved to ip ' + wlan_ip)
            else :
                self.__logger.error('--> Wlan name is not resolved')

            is_pingable = NetworkOutsideTester.is_pingable(self.__reference_usb_ip)
            if is_pingable :
                self.__logger.info('--> USB gadget ip pingable')
            else :
                self.__logger.error('--> USB gadget ip not pingable')
                result = False

            is_pingable = NetworkOutsideTester.is_pingable(self.__reference_eth_ip)
            if is_pingable :
                self.__logger.info('--> Ethernet ip pingable')
            else :
                self.__logger.error('--> Ethernet ip not pingable')
                result = False
            
            is_pingable = NetworkOutsideTester.is_pingable(wlan_ip)
            if is_pingable :
                self.__logger.info('--> Wlan ip pingable')
            else :
                self.__logger.error('--> Wlan ip not pingable')
                result = False

            if self.__shall_test_names : 
                is_pingable = NetworkOutsideTester.is_pingable("limelight.local")
                if is_pingable :
                    self.__logger.info('--> USB gadget name pingable')
                else :
                    self.__logger.error('--> USB gadget name not pingable')
                    result = False

            if self.__shall_test_names : 
                is_pingable = NetworkOutsideTester.is_pingable("limelight.eth.local")
                if is_pingable :
                    self.__logger.info('--> Ethernet name pingable')
                else :
                    self.__logger.error('--> Ethernet name not pingable')
                    result = False

       
            is_pingable = NetworkOutsideTester.is_pingable(self.__hostname + ".local")
            if is_pingable :
                self.__logger.info('--> Wlan name pingable')
            else :
                self.__logger.error('--> Wlan name not pingable')
                result = False
            
            can_login = NetworkOutsideTester.test_ssh(self.__reference_eth_ip, self.__user, self.__password, self.__shall_use_sshpass)
            if can_login :
                self.__logger.info('--> Login with ethernet ip is possible ')
            else :
                self.__logger.error('--> Login with ethernet ip is not possible')
                result = False

            can_login = NetworkOutsideTester.test_ssh(wlan_ip, self.__user, self.__password, self.__shall_use_sshpass)
            if can_login :
                self.__logger.info('--> Login with wlan ip is possible ')
            else :
                self.__logger.error('--> Login with wlan ip is not possible')
                result = False

            if self.__shall_test_names : 
                can_login = NetworkOutsideTester.test_ssh("limelight.eth.local", self.__user, self.__password, self.__shall_use_sshpass)
                if can_login :
                    self.__logger.info('--> Login with ethernet name is possible ')
                else :
                    self.__logger.error('--> Login with ethernet name is not possible')
                    result = False

     
            can_login = NetworkOutsideTester.test_ssh(self.__hostname + '.local', self.__user, self.__password, self.__shall_use_sshpass)
            if can_login :
                self.__logger.info('--> Login with wlan name is possible ')
            else :
                self.__logger.error('--> Login with wlan name is not possible')
                result = False

        return result
    
    def is_pingable(ip, timeout=5):
        """
        Check if the provided IP address responds to a single ping request.

        Args:
            ip (str): IP address to ping.
            timeout (int): Timeout in seconds for the ping response.

        Returns:
            bool: True if the host responds to ping, False otherwise.
        """
        # Choose ping command options based on OS
        count_flag = "-n" if system().lower() == "windows" else "-c"
        timeout_flag = "-w" if system().lower() == "windows" else "-W"
        
        try:
            result = run(
                ["ping", count_flag, "1", timeout_flag, str(timeout), ip],
                stdout=DEVNULL,
                stderr=DEVNULL
            )
            return result.returncode == 0
        except Exception:
            return False
        
    def resolve(hostname):
        """
        Resolve a hostname to an IPv4 address.

        Args:
            hostname (str): The hostname to resolve.

        Returns:
            str: The resolved IP address as a string, or an empty string if resolution fails.
        """
        result = ""
        try:
            ip = gethostbyname(hostname)
            result = ip
        except Exception as e:
            print(str(e))
            result = ""

        return result

    def test_ssh(hostname, user, password, usesshpass):
        """
        Attempt an SSH login to verify connectivity and credentials.

        Args:
            hostname (str): Host to SSH into.
            user (str): Username for SSH login.
            password (str): Password for SSH login.

        Returns:
            bool: True if SSH login succeeds, False otherwise.
        """
        result = False

        try:
            if usesshpass : 
                ssh = run(["sshpass", "-p", password, "ssh","-o","StrictHostKeyChecking=no", f"{user}@{hostname}", "exit"], stdout=PIPE, stderr=PIPE)
                if ssh.returncode != 0:
                    result = False
                else :
                    result = True
            else :
                ssh = run(["ssh","-o","StrictHostKeyChecking=no", f"{user}@{hostname}", "exit"], stdout=PIPE, stderr=PIPE)
                if ssh.returncode != 0:
                    result = False
                else :
                    result = True
        except Exception as e:
            print(str(e))
            result = False

        return result