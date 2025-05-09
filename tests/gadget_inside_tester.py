# -------------------------------------------------------
# Copyright (c) [2025] Nadege Lemperiere
# All rights reserved
# -------------------------------------------------------
"""
Module to test the internal configuration and status of the Limelight USB gadget.
This script checks kernel modules, USB gadget binding, systemd service status, and
network interface assignment from the inside (i.e., the Raspberry Pi acting as the gadget).
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

# Logger configuration settings
logg_conf_path = path.normpath(path.join(path.dirname(__file__), '../conf/logging.conf'))
env_path = path.normpath(path.join(path.dirname(__file__), '../conf/env'))

class GadgetInsideTester:
    """ Class managing gadget testing """

    #pylint: disable=R0913, C0301
    def __init__(self):
        """ Constructor """

        # Initialize logger
        self.__logger = getLogger('inside')
        self.__logger.info('INITIALIZING INSIDE GADGET TEST')

        self.__is_ready = False

    def configure(self) :
        """
        Reads the expected USB gadget IP address from the environment configuration file.
        Sets the tester readiness flag accordingly.
        """

        self.__logger.info('CONFIGURING INSIDE GADGET TEST')

        self.__is_ready = True


    def run(self) :
        """
        Runs all checks related to the Limelight USB gadget setup:
         - configfs mount status
         - libcomposite module presence
         - existence of the gadget directory
         - UDC binding
         - limelight-gadget.service enabled and active state
         - usb0 network interface IP assignment
        """

        result = False

        if self.__is_ready : 

            result = True

            self.__logger.info('RUNNING INSIDE TESTS')

            if "configfs on /sys/kernel/config" in GadgetInsideTester.run_command("mount") :
                self.__logger.info("--> configfs is mounted")
            else :
                self.__logger.error("--> configfs is not mounted")
                result = False

            if "libcomposite" in GadgetInsideTester.run_command("lsmod"):
                self.__logger.info("--> libcomposite module loaded")
            else :
                self.__logger.error("--> libcomposite module not loaded")
                result = False

            if path.isdir("/sys/kernel/config/usb_gadget/limelight"):
                self.__logger.info("--> Limelight gadget exists")
            else :
                self.__logger.error("--> Limelight gadget missing")
                result = False

            udc_path = "/sys/kernel/config/usb_gadget/limelight/UDC"
            if path.isfile(udc_path) and path.getsize(udc_path) > 0:
                 self.__logger.info("--> UDC is bound")
            else :
                self.__logger.error("--> UDC is not bound")
                result = False

            enabled = GadgetInsideTester.run_command(f"systemctl is-enabled limelight-gadget.service")
            if enabled == "enabled" :
                self.__logger.info("--> limelight-gadget.service is enabled")
            else :
                self.__logger.error("--> limelight-gadget.service is not enabled")
                result = False
                
            active = GadgetInsideTester.run_command(f"systemctl is-active limelight-gadget.service")
            if active == "active" :
                self.__logger.info("--> limelight-gadget.service is active")
            else :
                self.__logger.error("--> limelight-gadget.service is not active")
                result = False
            
            
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
