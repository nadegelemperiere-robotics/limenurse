# -------------------------------------------------------
# Copyright (c) [2025] Nadege Lemperiere
# All rights reserved
# -------------------------------------------------------
"""
Script to test the routing configuration for Limelight
connectivity through both USB and Ethernet interfaces.
Includes tests for routing from inside and outside the
Pi network configuration.
"""
# -------------------------------------------------------
# Nadège LEMPERIERE, @29th April 2025
# Latest revision: 29th April 2025
# -------------------------------------------------------

# System includes
from logging                        import config, getLogger
from os                             import path

# Click includes
from click                          import option, group

# Local includes
from routing_outside_tester         import RoutingOutsideTester
from routing_inside_tester          import RoutingInsideTester

# Logger configuration settings
logg_conf_path = path.normpath(path.join(path.dirname(__file__), '../conf/logging.conf'))

class RoutingTester:
    """Handles execution of routing tests for Limelight integration.

    This class manages separate testing routines depending on whether
    the traffic is originating from inside (the Pi) or outside (connected device),
    and delegates testing to the appropriate tester implementation.
    """

    sSourceOutside  = "outside"
    sSourceInside = "inside"

    #pylint: disable=R0913, C0301
    def __init__(self):
        """ Constructor """

        # Initialize logger
        self.__logger = getLogger()
        self.__logger.info('INITIALIZING ROUTING TEST')

        self.__outside = RoutingOutsideTester()
        self.__inside = RoutingInsideTester()

    def configure(self, source, platform) :
        """Prepare the test environment based on selected source direction.

        Args:
            source (str): Either 'inside' or 'outside' indicating test source perspective.
            platform (str): OS on which outside tests are executed (windows, ios, linux)
        """

        self.__logger.info('CONFIGURING ROUTING TEST')

        if source == RoutingTester.sSourceInside :
            self.__logger.info('--> Setting inside tests up')
            self.__inside.configure()
        elif source == RoutingTester.sSourceOutside :
            self.__logger.info('--> Setting outside tests up')
            self.__outside.configure(platform)
        else :
            self.__logger.error('--> Unknown test source : Giving up')

        self.__source = source

    def run(self) :
        """Execute the configured routing test and log the result."""

        result = False

        self.__logger.info('RUNNING ROUTING TESTS')

        if self.__source == RoutingTester.sSourceInside :
            result = self.__inside.run()
        elif self.__source == RoutingTester.sSourceOutside :
            result = self.__outside.run()

        if result :
            self.__logger.info('--> Tests sucessfully executed')
        else :
            self.__logger.error('--> Tests failed - See logs for more info')


# pylint: disable=W0107
# Main function using Click for command-line options
@group()
def main():
    """Main CLI entry point for the routing tester script."""
    pass
# pylint: enable=W0107, W0719

# pylint: disable=R0913
@main.command()
@option('--source')
@option('--platform')
def run(source, platform):
    """Run the routing test for a given traffic source.

    Args:
        source (str): The origin of the traffic for testing, either 'inside' or 'outside'.
        platform (str): OS on which outside tests are executed (windows, ios, linux)
    """

    tester = RoutingTester()
    tester.configure(source, platform)
    tester.run()

if __name__ == "__main__":
    config.fileConfig(logg_conf_path)
    main()
