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
from re                             import search
from subprocess                     import check_output, CalledProcessError, DEVNULL
from psutil                         import process_iter, NoSuchProcess, AccessDenied

# Logger configuration settings
logg_conf_path = path.normpath(path.join(path.dirname(__file__), '../conf/logging.conf'))
env_path = path.normpath(path.join(path.dirname(__file__), '../conf/env'))

class RoutingInsideTester:
    """ 
    Class for testing internal routing configurations for the Limelight gadget.
    This tester checks that both Ethernet and USB gateway IPs are correctly configured 
    and available for the routing setup. The configuration is read from the environment file.
    """

    #pylint: disable=R0913, C0301
    def __init__(self):
        """ Constructor """

        # Initialize logger
        self.__logger = getLogger('inside')
        self.__logger.info('INITIALIZING INSIDE ROUTING TEST')

        self.__is_ready = False

    def configure(self) :
        """
        Load and verify the internal routing configuration from the environment file.
        Sets reference IPs for both Ethernet and USB, and determines readiness to run the test.
        """

        self.__logger.info('CONFIGURING INSIDE ROUTING TEST')

        self.__is_ready = False

        self.__reference_eth_ip = ""
        with open(env_path, 'r') as file:
            match = search(r'ETH_IP_GATEWAY=([\d\.]+)', file.read())
            if match : 
                self.__reference_eth_ip = match.group(1)

        self.__reference_usb_ip = ""
        with open(env_path, 'r') as file:
            match = search(r'USB_IP_GATEWAY=([\d\.]+)', file.read())
            if match : 
                self.__reference_usb_ip = match.group(1)

        if len(self.__reference_eth_ip) != 0 and len(self.__reference_usb_ip) != 0 :
            self.__is_ready = True


    def run(self) :
        """
        Executes the internal routing test if configuration is ready.
        Logs the test action and returns a boolean indicating success.
        """

        result = False

        if self.__is_ready : 

            result = True

            self.__logger.info('RUNNING INSIDE TESTS')

            enabled = RoutingInsideTester.run_command(f"systemctl is-enabled limelight-routing.service")
            if enabled == "enabled" :
                self.__logger.info("--> limelight-routing.service is enabled")
            else :
                self.__logger.error("--> limelight-routing.service is not enabled")
                result = False
                
            active = RoutingInsideTester.run_command(f"systemctl is-active limelight-routing.service")
            if active == "active" :
                self.__logger.info("--> limelight-routing.service is active")
            else :
                self.__logger.error("--> limelight-routing.service is not active")
                result = False   

            running = RoutingInsideTester.is_python_command_running("udp_forwarder.py")
            if running :
                self.__logger.info("--> Python forwarder is running")
            else :
                self.__logger.error("--> Python forwarder is not running")
                result = False   

            has_error = RoutingInsideTester.file_contains_error("/var/log/udp_forwarder.log")
            if not has_error :
                self.__logger.info("--> No error in forwarder log")
            else :
                self.__logger.error("--> Error found in forwarder log")
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

    def run_command(command):
        """
        Executes a shell command and returns its output as a decoded string.
        Returns an empty string on failure.
        """
        try:
            output = check_output(command, shell=True, stderr=DEVNULL)
            return output.decode().strip()
        except CalledProcessError:
            return ""


    def file_contains_error(file_path):

        result = False

        if not path.isfile(file_path):
            result = True

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if '- ERROR -' in line:
                        result = True
        except Exception as e:
            result = True

        return result
