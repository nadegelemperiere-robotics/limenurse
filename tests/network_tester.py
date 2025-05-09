# -------------------------------------------------------
# Copyright (c) [2025] Nadege Lemperiere
# All rights reserved
# -------------------------------------------------------
"""
Test limelight network configuration
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
from network_outside_tester         import NetworkOutsideTester
from network_inside_tester          import NetworkInsideTester

# Logger configuration settings
logg_conf_path = path.normpath(path.join(path.dirname(__file__), '../conf/logging.conf'))

class NetworkTester:
    """Class responsible for orchestrating and executing network connectivity tests 
    from either an inside or outside network context using appropriate tester classes."""

    sSourceOutside  = "outside"
    sSourceInside = "inside"

    #pylint: disable=R0913, C0301
    def __init__(self):
        """Initialize the NetworkTester by setting up logging and creating tester instances for both contexts."""

        # Initialize logger
        self.__logger = getLogger()
        self.__logger.info('%s', 'INITIALIZING NETWORK TEST')

        self.__outside = NetworkOutsideTester()
        self.__inside = NetworkInsideTester()

    def configure(self, source, platform, user, hostname, password) :
        """Configure the appropriate network tester based on the specified source.

        Args:
            source (str): Indicates whether tests are run from 'inside' or 'outside' the network.
            platform (str): OS on which outside tests are executed (windows, ios, linux)
            user (str): SSH username (used only for outside tests).
            hostname (str): Hostname or IP address of the remote machine (used only for outside tests).
            password (str): SSH password (used only for outside tests).
        """

        self.__logger.info('%s', 'CONFIGURING NETWORK TEST')

        if source == NetworkTester.sSourceInside :
            self.__logger.info('%s', '--> Setting inside tests up')
            self.__inside.configure()
        elif source == NetworkTester.sSourceOutside :
            self.__logger.info('%s', '--> Setting outside tests up')
            self.__outside.configure(platform, user, hostname, password)
        else :
            self.__logger.error('%s', '--> Unknown test source : Giving up')

        self.__source = source

    def run(self) :
        """Execute the configured network tests and log the results."""

        result = False

        self.__logger.info('%s', 'RUNNING NETWORK TESTS')

        if self.__source == NetworkTester.sSourceInside :
            result = self.__inside.run()
        elif self.__source == NetworkTester.sSourceOutside :
            result = self.__outside.run()

        if result :
            self.__logger.info('%s', '--> Tests sucessfully executed')
        else :
            self.__logger.error('%s', '--> Tests failed - See logs for more info')


# pylint: disable=W0107
# Main function using Click for command-line options
@group()
def main():
    """Main command group for network testing CLI tool."""
    pass
# pylint: enable=W0107, W0719

# pylint: disable=R0913
@main.command()
@option('--source')
@option('--platform')
@option('--user')
@option('--hostname')
@option('--password')
def run(source, platform, user, hostname, password):
    """Run the network tests with specified configuration parameters."""

    tester = NetworkTester()
    tester.configure(source, platform, user, hostname, password)
    tester.run()

if __name__ == "__main__":
    config.fileConfig(logg_conf_path)
    main()
