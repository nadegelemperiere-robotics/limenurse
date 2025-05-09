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
from subprocess                     import check_output, CalledProcessError, DEVNULL
from re                             import search
from psutil                         import process_iter, NoSuchProcess, AccessDenied

# Logger configuration settings
logg_conf_path = path.normpath(path.join(path.dirname(__file__), '../conf/logging.conf'))
env_path = path.normpath(path.join(path.dirname(__file__), '../conf/env'))

class NetworkInsideTester:
    """
    Performs validation of the internal network setup for the Limelight gadget.

    This class reads network environment configuration values and runs checks to ensure that:
    - The expected USB and Ethernet gateway IPs are defined.
    - The Avahi hosts file contains the correct IP-to-hostname mappings.
    - The dnsmasq and avahi-daemon services are both enabled and running.

    Logging is used to trace steps and failures.
    """

    #pylint: disable=R0913, C0301
    def __init__(self):
        """
        Constructor.

        Initializes the logger and sets the initial readiness state.
        """
        # Initialize logger
        self.__logger = getLogger('inside')
        self.__logger.info('INITIALIZING INSIDE NETWORK TEST')

        self.__is_ready = False

    def configure(self) :
        """
        Load IP address configuration.

        Reads expected IP addresses from the environment configuration file for USB and Ethernet gateways.
        Marks the tester as ready if both are successfully retrieved.
        """
        self.__logger.info('CONFIGURING INSIDE NETWORK TEST')

        self.__is_ready = False

        # Read the Ethernet gateway IP address from the environment file
        self.__reference_eth_ip = ""
        with open(env_path, 'r') as file:
            match = search(r'ETH_IP_GATEWAY=([\d\.]+)', file.read())
            if match : 
                self.__reference_eth_ip = match.group(1)

        # Read the USB gateway IP address from the environment file
        self.__reference_usb_linux_ip = ""
        with open(env_path, 'r') as file:
            match = search(r'USB_IP_GATEWAY_LINUX=([\d\.]+)', file.read())
            if match : 
                self.__reference_usb_linux_ip = match.group(1)

        # Read the USB gateway IP address from the environment file
        self.__reference_usb_windows_ip = ""
        with open(env_path, 'r') as file:
            match = search(r'USB_IP_GATEWAY_WINDOWS=([\d\.]+)', file.read())
            if match : 
                self.__reference_usb_windows_ip = match.group(1)
        

        # Set readiness to True only if both IP addresses are found
        if len(self.__reference_eth_ip) != 0 and len(self.__reference_usb_windows_ip) != 0 and len(self.__reference_usb_linux_ip) != 0:
            self.__is_ready = True


    def run(self) :
        """
        Execute the internal network validation tests.

        Tests include:
        - Existence of the Avahi hosts file.
        - Validation of host declarations for the Limelight USB and Ethernet interfaces.
        - Checks that dnsmasq and avahi-daemon services are both enabled and active.

        Returns:
            bool: True if all checks pass, otherwise False.
        """
        result = False

        if self.__is_ready : 
            result = True

            self.__logger.info('RUNNING INSIDE TESTS')

            # Check that network services are active
            enabled = NetworkInsideTester.run_command(f"systemctl is-enabled limelight-address.service")
            if enabled == "enabled" :
                self.__logger.info("--> limelight-address.service is enabled")
            else :
                self.__logger.error("--> limelight-address.service is not enabled")
                result = False

            
            active = NetworkInsideTester.run_command(f"systemctl is-active limelight-address.service")
            if active == "active" :
                self.__logger.info("--> limelight-address.service is active")
            else :
                self.__logger.error("--> limelight-address.service is not active")
                result = False

            # Check if interfaces IP are correct
            ip_output = NetworkInsideTester.run_command("ip addr show eth0")
            match = search(r"inet (\d+\.\d+\.\d+\.\d+)/", ip_output)
            if match:
                current_ip = match.group(1)
                if current_ip == self.__reference_eth_ip:
                    self.__logger.info("eth0 has expected IP address: " + self.__reference_eth_ip)
                else:
                    self.__logger.error("eth0 has unexpected IP address: " + current_ip + " (expected " + self.__reference_eth_ip + ")")
            else:
                self.__logger.error("eth0 interface not found or no IP address assigned")

            ip_output = NetworkInsideTester.run_command("ip addr show usb0")
            match = search(r"inet (\d+\.\d+\.\d+\.\d+)/", ip_output)
            if match:
                current_ip = match.group(1)
                if current_ip == self.__reference_usb_linux_ip:
                    self.__logger.info("usb0 has expected IP address: " + self.__reference_usb_linux_ip)
                else:
                    self.__logger.error("usb0 has unexpected IP address: " + current_ip + " (expected " + self.__reference_usb_linux_ip + ")")
            else:
                self.__logger.error("usb0 interface not found or no IP address assigned")

            ip_output = NetworkInsideTester.run_command("ip addr show usb1")
            match = search(r"inet (\d+\.\d+\.\d+\.\d+)/", ip_output)
            if match:
                current_ip = match.group(1)
                if current_ip == self.__reference_usb_windows_ip:
                    self.__logger.info("usb1 has expected IP address: " + self.__reference_usb_windows_ip)
                else:
                    self.__logger.error("usb1 has unexpected IP address: " + current_ip + " (expected " + self.__reference_usb_windows_ip + ")")
            else:
                self.__logger.error("usb1 interface not found or no IP address assigned")

            # Check if dnsmasq service is enabled
            enabled = NetworkInsideTester.run_command(f"systemctl is-enabled dnsmasq.service")
            if enabled == "enabled" :
                self.__logger.info("--> dnsmasq.service is enabled")
            else :
                self.__logger.error("--> dnsmasq.service is not enabled")
                result = False
                
            # Check if dnsmasq service is active
            active = NetworkInsideTester.run_command(f"systemctl is-active dnsmasq.service")
            if active == "active" :
                self.__logger.info("--> dnsmasq.service is active")
            else :
                self.__logger.error("--> dnsmasq.service is not active")
                result = False

            # Check avahi is still active
            enabled = NetworkInsideTester.run_command(f"systemctl is-enabled avahi-daemon.service")
            if enabled == "enabled" :
                self.__logger.info("--> avahi-daemon.service is enabled")
            else :
                self.__logger.error("--> avahi-daemon.service is not enabled")
                result = False
                
            active = NetworkInsideTester.run_command(f"systemctl is-active avahi-daemon.service")
            if active == "active" :
                self.__logger.info("--> avahi-daemon.service is active")
            else :
                self.__logger.error("--> avahi-daemon.service is not active")
                result = False   

            # Check custom dns management is active
            enabled = NetworkInsideTester.run_command(f"systemctl is-enabled limelight-dns.service")
            if enabled == "enabled" :
                self.__logger.info("--> limelight-dns.service is enabled")
            else :
                self.__logger.error("--> limelight-dns.service is not enabled")
                result = False
                
            active = NetworkInsideTester.run_command(f"systemctl is-active limelight-dns.service")
            if active == "active" :
                self.__logger.info("--> limelight-dns.service is active")
            else :
                self.__logger.error("--> limelight-dns.service is not active")
                result = False   

            # Check that the python script is running
            running = NetworkInsideTester.is_python_command_running("name_resolver.py")
            if running :
                self.__logger.info("--> Python forwarder is running")
            else :
                self.__logger.error("--> Python forwarder is not running")
                result = False   

            has_error = NetworkInsideTester.file_contains_error("/var/log/name_resolver.log")
            if not has_error :
                self.__logger.info("--> No error in forwarder log")
            else :
                self.__logger.error("--> Error found in  forwarder log")
                result = False   
            
            return result
        
    
    def is_python_command_running(target_cmd):
        
        result = False
        
        for proc in process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'python' in proc.info['name'] and any(target_cmd in part for part in proc.info['cmdline']):
                    result = True
            except (NoSuchProcess, AccessDenied):
                continue

        return result
    
    def file_contains_error(file_path):

        result = True

        if not path.isfile(file_path):
            result = True

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if ' - ERROR -' in line:
                        result = False
        except Exception as e:
            result = False

        return result

            

    def run_command(command):
        """
        Run a shell command and return its output.

        Args:
            command (str): The command string to execute.

        Returns:
            str: Output of the command on success, empty string on failure.
        """
        try:
            output = check_output(command, shell=True, stderr=DEVNULL)
            return output.decode().strip()
        except CalledProcessError:
            return ""
