# -------------------------------------------------------
# Copyright (c) [2025] Nadege Lemperiere
# All rights reserved
# -------------------------------------------------------
"""
This script provides a command-line interface to validate the configuration
of a Raspberry Pi acting as a USB gadget for Limelight integration.
It supports tests for both internal (host-side) and external (device-side)
configurations.
"""
# -------------------------------------------------------
# Nadège LEMPERIERE, @30th April 2025
# Latest revision: 30th April 2025
# -------------------------------------------------------

# System includes
from logging                        import config, getLogger
from os                             import path

# Click includes
from click                          import option, group

# Local includes
from gadget_outside_tester          import GadgetOutsideTester
from gadget_inside_tester           import GadgetInsideTester

# Logger configuration settings
logg_conf_path = path.normpath(path.join(path.dirname(__file__), '../conf/logging.conf'))

class GadgetTester:
    """
    Handles testing logic for USB gadget configurations.

    Depending on the provided source, the class configures and runs
    tests for either the 'inside' (device/gadget) or 'outside' (host/PC) perspective.
    """

    sSourceOutside  = "outside"
    sSourceInside = "inside"

    #pylint: disable=R0913, C0301
    def __init__(self):
        """
        Initialize the GadgetTester instance.

        This sets up logging and instantiates both inside and outside tester
        components for later use.
        """
        # Initialize logger
        self.__logger = getLogger()
        self.__logger.info('INITIALIZING GADGET TEST')

        # Create tester instances for outside and inside gadgets
        self.__outside = GadgetOutsideTester()
        self.__inside = GadgetInsideTester()

    def configure(self, source) :
        """
        Configure the test setup for a specific source.

        Args:
            source (str): Either 'inside' or 'outside'.

        Based on the selected source, this prepares the corresponding tester instance
        for execution.
        """
        self.__logger.info('CONFIGURING GADGET TEST')

        # Determine which tester to configure based on the source parameter
        if source == GadgetTester.sSourceInside :
            self.__logger.info('--> Setting inside tests up')
            self.__inside.configure()
        elif source == GadgetTester.sSourceOutside :
            self.__logger.info('--> Setting outside tests up')
            self.__outside.configure()
        else :
            # Log an error if the source is not recognized
            self.__logger.error('--> Unknown test source : Giving up')

        # Store the source for later use during test run
        self.__source = source

    def run(self) :
        """
        Execute the tests for the configured source.

        Returns:
            bool: True if the tests complete successfully, False otherwise.
        """
        result = False

        self.__logger.info('RUNNING GADGET TESTS')

        # Run the appropriate tests based on the stored source
        if self.__source == GadgetTester.sSourceInside :
            result = self.__inside.run()
        elif self.__source == GadgetTester.sSourceOutside :
            result = self.__outside.run()

        # Log the outcome of the test execution
        if result :
            self.__logger.info('--> Tests sucessfully executed')
        else :
            self.__logger.error('--> Tests failed - See logs for more info')


# pylint: disable=W0107
# Main function using Click for command-line options
@group()
def main():
    """
    Click command group for gadget testing CLI.
    """
    pass
# pylint: enable=W0107, W0719

# pylint: disable=R0913
@main.command()
@option('--source')
def run(source):
    """
    Run the gadget test command with the provided source.

    Args:
        source (str): The source perspective for the test ('inside' or 'outside').
    """

    tester = GadgetTester()
    tester.configure(source)
    tester.run()

if __name__ == "__main__":
    config.fileConfig(logg_conf_path)
    main()
