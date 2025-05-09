# -------------------------------------------------------
# Copyright (c) [2025] Nadege Lemperiere
# All rights reserved
# -------------------------------------------------------
"""
This script implements a mDNS server to manage name 
resolution on each of the Pi interfaces
"""
# -------------------------------------------------------
# Nadège LEMPERIERE, @7th May 2025
# Latest revision: 7th May 2025
# -------------------------------------------------------


# System includes
from socket             import inet_ntoa, inet_aton, socket, AF_INET, SOCK_DGRAM
from fcntl              import ioctl
from struct             import pack
from time               import sleep
from argparse           import ArgumentParser
from signal             import signal, SIGINT, SIGTERM
from logging            import info, error, DEBUG, Formatter, getLogger
from logging.handlers   import RotatingFileHandler

# Zeroconf includes
from zeroconf           import Zeroconf, ServiceInfo, IPVersion


class NameResolver :
    
    def __init__(self):
        """Initialize the UdpForwarder with default None sockets and parameters."""
        self.__is_running = False

        self.__dns  = None
        self.__services = []

        self.__interfaces = [ ]

    def configure(self, usb, eth) :
        """
        Configure the forwarder with source and destination IPs and interfaces.

        Parameters:
        - usb: Name to publish on usb interface 
        - eth: Name to publish on ethernet interface
        """

        self.__services = []
        self.__dns = Zeroconf(ip_version=IPVersion.V4Only)

        self.__interfaces = [ 
            (usb, ["usb0", "usb1"]),
            (eth, ["eth0"])
        ]

        handler = RotatingFileHandler('/var/log/name_forwarder.log', maxBytes=5*1024*1024, backupCount=3)
        formatter = Formatter('%(asctime)s - line %(lineno)d - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        getLogger().setLevel(DEBUG)
        getLogger().addHandler(handler)

        self.__is_running = True

    def start(self) :
        """
        Initialize and bind raw and UDP sockets for forwarding.

        Sets up:
        - Raw sockets bound to input interfaces to capture all IPv4 packets.
        - Raw socket bound to output interface for backward direction.
        - UDP datagram sockets for sending and receiving broadcast packets.
        """

        result = True

        info(f" Starting forwarder")

        signal(SIGTERM, self.__handle_signal)
        signal(SIGINT, self.__handle_signal)

        self.__services = []

        for name, interfaces in self.__interfaces :

            ips = []
            for interface in interfaces :
                try :  
                    ip = NameResolver.__ip_address(interface)
                    if not ip : raise Exception()
                    ips.append(inet_aton(ip))

                except Exception :
                    result = False 
                    error("No IP found for interface " + interface)

            try : 
                if len(ips) != 0 : 
                    service = ServiceInfo(
                        type_="_http._tcp.local.",
                        name=f"{name}._http._tcp.local.",
                        addresses=ips,
                        port=80,  # Dummy port — ignored for name resolution
                        properties={},
                        server=name,
                    )
                    self.__dns.register_service(service)
                    self.__services.append(service)
                    info(" Publishing name " + name + " on " + interface)

            except Exception as e :
                result = False 
                error("Failed to register " + interface + " : " + str(e))
        
        return (result or not self.__is_running)

    def process(self):
        """
        Keep publication alive.
        Update services to keep name active
        """
        i_iteration = 0
        while self.__is_running:

            if i_iteration % 6 == 0 :

                services = []

                for name, interfaces in self.__interfaces :

                    ips = []
                    for interface in interfaces :
                        try :  
                            ip = NameResolver.__ip_address(interface)
                            if not ip : raise Exception()
                            ips.append(inet_aton(ip))

                        except Exception :
                            error("No IP found for interface " + interface)

                    try : 
                        if len(ips) != 0 : 
                            matching_service = next((s for s in self.__services if s.server == name), None)
                            if matching_service :
                                shall_update = False
                                for ip in ips :
                                    if not ip in matching_service.addresses :
                                        info(f"New IP found for {name} changed from {ip}, updating service.")
                                        shall_update = True
                                for address in matching_service.addresses :
                                    if not address in ips :
                                        info(f"IP no {address} longer valid for {name}, updating service.")
                                        shall_update = True
                                
                                if shall_update :

                                    # Unregister old and register new
                                    self.__dns.unregister_service(matching_service)
                                    self.__services.remove(matching_service)

                                    new_service = ServiceInfo(
                                        type_="_http._tcp.local.",
                                        name=f"{name}._http._tcp.local.",
                                        addresses=ips,
                                        port=80,
                                        properties={},
                                        server=name,
                                    )
                                    self.__dns.register_service(new_service)
                                    services.append(new_service)
                                else:
                                    self.__dns.update_service(matching_service)
                                    services.append(matching_service)
                                    for ip in ips : 
                                        info(f"Refreshed service for {name} at {ip}")
                            else:
                                # No service published yet, possibly reinitialization
                                new_service = ServiceInfo(
                                    type_="_http._tcp.local.",
                                    name=f"{name}._http._tcp.local.",
                                    addresses=ips,
                                    port=80,
                                    properties={},
                                    server=name,
                                )
                                self.__dns.register_service(new_service)
                                services.append(new_service)
                                for ip in ips : 
                                    info(f"Registered new service for {name} at {ip}")

                    except Exception as e:
                        error(f"Error updating service for {name}: {e}")

                # Replace the services list with updated references
                self.__services = services

            i_iteration = i_iteration+ 1    
            sleep(5)

    def stop(self) :
        """Stop all names publication."""

        info("Stopping")

        for service in self.__services:
            self.__dns.unregister_service(service)
        self.__dns.close()

    def __handle_signal(self, signum, frame):
        """Handle termination signals to cleanly stop the forwarder."""
        info("Signal received, exiting...")
        self.__is_running = False

    def __ip_address(ifname):
        try:
            s = socket(AF_INET, SOCK_DGRAM)
            return inet_ntoa(
                ioctl(
                    s.fileno(),
                    0x8915,
                    pack('256s', ifname[:15].encode())
                )[20:24]
            )
        except Exception:
            return None

if __name__ == "__main__":

    # Instantiate the UDP forwarder
    resolver = NameResolver()

    # Command-line interface to specify source/destination IPs and interfaces
    parser = ArgumentParser(description="Name resolver for Limelight access through multiple interfaces")
    parser.add_argument("--usb", dest="usb", required=True, help="Name to publish on usb gadget interface")
    parser.add_argument("--eth", dest="eth", required=True, help="Name to publish on ethernet interface")


    args = parser.parse_args()

    # Configure and start the forwarder
    resolver.configure(args.usb, args.eth)

    started = False
    while not started : 
        started = resolver.start()
        sleep(1)
    
    info("mDNS resolver running. Press Ctrl+C to stop.")
    resolver.process()
    resolver.stop()
    