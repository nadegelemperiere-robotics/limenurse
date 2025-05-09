# -------------------------------------------------------
# Copyright (c) [2025] Nadege Lemperiere
# All rights reserved
# -------------------------------------------------------
"""
This script implements a UDP forwarder that bridges UDP broadcast packets between multiple network interfaces.
It is designed to facilitate communication between Limelight devices across different network segments by
capturing UDP broadcasts on specified interfaces and forwarding them appropriately to other interfaces and IPs.
"""
# -------------------------------------------------------
# Nadège LEMPERIERE, @4th May 2025
# Latest revision: 4th May 2025
# -------------------------------------------------------

from fcntl              import ioctl
from struct             import pack, unpack
from socket             import socket, AF_INET, AF_PACKET, SOCK_RAW, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST, inet_ntoa, ntohs
from select             import select
from threading          import Thread
from argparse           import ArgumentParser
from signal             import signal, SIGINT, SIGTERM
from struct             import unpack
from logging            import info, error, debug, DEBUG, Formatter, getLogger
from logging.handlers   import RotatingFileHandler


class UdpForwarder :
    
    def __init__(self):
        """Initialize the UdpForwarder with default None sockets and parameters."""
        self.__is_running = False

        # Sockets toward limelight
        self.__forward_sending_socket = None
        self.__forward_receiving_socket1 = None
        self.__forward_receiving_socket2 = None
        self.__forward_receiving_socket3 = None

        # Sockets from limelight
        self.__backward_sending_socket1 = None
        self.__backward_sending_socket2 = None
        self.__backward_sending_socket3 = None
        self.__backward_receiving_socket = None

        # Gateways IP (limelight and PI)
        self.__gateway1 = None
        self.__gateway2 = None
        self.__gateway3 = None
        self.__gateway_out = None

        # Interfaces names on PI
        self.__interface1 = None
        self.__interface2 = None
        self.__interface3 = None
        self.__interface_out = None

        # Senders and receivers IPs on the gateways networks
        self.__ip1 = None
        self.__ip2 = None
        self.__ip3 = None
        self.__ip_out = None

    def configure(self, in_ip1, in_ip2, in_ip3, out_ip, in_int1, in_int2, in_int3, out_int, port) :
        """
        Configure the forwarder with source and destination IPs and interfaces.

        Parameters:
        - in_ip1, in_ip2, in_ip3: Gateway IPs for the two input interfaces (source networks).
        - out_ip: Gateway IP for the output interface (destination network).
        - in_int1, in_int2, in_int3: Network interfaces to listen on for incoming UDP packets.
        - out_int: Network interface to forward UDP packets to.
        - port: UDP port number used for forwarding.
        """

        self.__gateway1 = in_ip1
        self.__gateway2 = in_ip2
        self.__gateway3 = in_ip3
        self.__gateway_out = out_ip

        self.__interface1 = in_int1
        self.__interface2 = in_int2
        self.__interface3 = in_int3
        self.__interface_out = out_int

        self.__ip1 = None
        self.__ip2 = None
        self.__ip3 = None
        self.__ip_out = None

        self.__port = port

        self.__is_running = True

        handler = RotatingFileHandler('/var/log/udp_forwarder.log', maxBytes=5*1024*1024, backupCount=3)
        formatter = Formatter('%(asctime)s - line %(lineno)d - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        getLogger().setLevel(DEBUG)
        getLogger().addHandler(handler)

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

        try :
            # Raw socket to receive all IPv4 packets on interface1
            self.__forward_receiving_socket1 = socket(AF_PACKET, SOCK_RAW, ntohs(0x0800))
            self.__forward_receiving_socket1.bind((self.__interface1,0))
            self.__forward_receiving_socket1.setblocking(0)
            info(f" Raw forward receiving socket 1 bound to {self.__interface1}")
        except Exception as e:
            error(f"Failed to bind raw forward socket 1 : {e}")
            result = False
        
        try :
            # Raw socket to receive all IPv4 packets on interface2
            self.__forward_receiving_socket2 = socket(AF_PACKET, SOCK_RAW, ntohs(0x0800))
            self.__forward_receiving_socket2.bind((self.__interface2,0))
            self.__forward_receiving_socket2.setblocking(0)
            info(f" Raw forward receiving socket 2 bound to {self.__interface2}")
        except Exception as e:
            error(f"Failed to bind raw forward socket 2 : {e}")
            result = False

        try :
            # Raw socket to receive all IPv4 packets on interface3
            self.__forward_receiving_socket3 = socket(AF_PACKET, SOCK_RAW, ntohs(0x0800))
            self.__forward_receiving_socket3.bind((self.__interface3,0))
            self.__forward_receiving_socket3.setblocking(0)
            info(f" Raw forward receiving socket 3 bound to {self.__interface3}")
        except Exception as e:
            error(f"Failed to bind raw forward socket 3 : {e}")
            result = False
        
        try :
            # Raw socket to receive all IPv4 packets on output interface for backward forwarding
            self.__backward_receiving_socket = socket(AF_PACKET, SOCK_RAW, ntohs(0x0800))
            self.__backward_receiving_socket.bind((self.__interface_out,0))
            self.__backward_receiving_socket.setblocking(0)
            info(f" Raw backward receiving socket bound to {self.__interface_out}")
        except Exception as e:
            error(f"Failed to bind raw forward socket 1 : {e}")
            result = False
        
        try:
            # UDP socket for sending forwarded packets out
            # The port shall be fixed because limelight does not take care of
            # the sender port and sends broadcast UDP packet back to port 5809
            self.__forward_sending_socket = socket(AF_INET, SOCK_DGRAM)
            self.__forward_sending_socket.bind(("0.0.0.0",self.__port))
            self.__forward_sending_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        except Exception as e:
            error(f"Failed to create forward sending socket: {e}")
            result = False
        
        try:
            # UDP socket for sending backward packets to gateway1
            self.__backward_sending_socket1 = socket(AF_INET, SOCK_DGRAM)
            self.__backward_sending_socket1.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        except Exception as e:
            error(f"Failed to create backward sending socket 1: {e}")
            result = False
        
        try:
            # UDP socket for sending backward packets to gateway2
            self.__backward_sending_socket2 = socket(AF_INET, SOCK_DGRAM)
            self.__backward_sending_socket2.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        except Exception as e:
            error(f"Failed to create backward sending socket 2: {e}")
            result = False
        try:
            # UDP socket for sending backward packets to gateway2
            self.__backward_sending_socket3 = socket(AF_INET, SOCK_DGRAM)
            self.__backward_sending_socket3.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        except Exception as e:
            error(f"Failed to create backward sending socket 3: {e}")
            result = False
        
        info(f"Forwarding all UDP packets received on {self.__interface1} to {self.__interface_out} on port {self.__port}")
        info(f"Forwarding all UDP packets received on {self.__interface2} to {self.__interface_out} on port {self.__port}")
        info(f"Forwarding all UDP packets received on {self.__interface3} to {self.__interface_out} on port {self.__port}")
        info(f"Forwarding all UDP packets received on {self.__interface_out} to {self.__interface1} on same port")
        info(f"Forwarding all UDP packets received on {self.__interface_out} to {self.__interface2} on same port")
        info(f"Forwarding all UDP packets received on {self.__interface_out} to {self.__interface3} on same port")

        return (result or not self.__is_running)

    def process_forward1(self):
        """
        Continuously process UDP packets received on interface1 and forward them to the output interface.
        """
        while self.__is_running:
            # Check/rebind socket if needed
            if (
                self.__forward_receiving_socket1 is None
                or not self.__interface_is_up(self.__interface1)
            ):
                self.__forward_receiving_socket1 = self.__rebind_socket(self.__forward_receiving_socket1, self.__interface1)
                if self.__forward_receiving_socket1 is None:
                    from time import sleep
                    sleep(1)
                    continue
            try:
                ready, _, _ = select([self.__forward_receiving_socket1], [], [], 1.0)
            except Exception as e:
                error(f"Select error on forward1: {e}")
                continue
            if ready:
                try:
                    pkt, _ = self.__forward_receiving_socket1.recvfrom(65535)
                    ip_header = pkt[14:34]
                    udp_header = pkt[34:42]
                    iph = unpack('!BBHHHBBH4s4s', ip_header)
                    protocol = iph[6]
                    if protocol != 17:
                        continue  # Not UDP
                    src_addr = inet_ntoa(iph[8])
                    dst_addr = inet_ntoa(iph[9])
                    self.__ip1 = src_addr
                    udph = unpack('!HHHH', udp_header)
                    src_port, dst_port = udph[0], udph[1]
                    if dst_port in (53, 67, 68, 5353):
                        debug(f"[SKIP] Skipping UDP packet to reserved port {dst_port}")
                        continue
                    data = pkt[42:]
                    debug(f"[RECV] UDP {src_addr}:{src_port} → {dst_addr}:{dst_port}, {len(data)} bytes")
                    try:
                        target_ip = self.__gateway_out
                        if self.__ip_out is not None:
                            target_ip = self._ip_out
                        self.__forward_sending_socket.sendto(data, (target_ip, dst_port))
                        debug(f"[SEND] Forwarded to {target_ip}:{dst_port}")
                    except Exception as e:
                        error(f"Failed to forward: {e}")
                except OSError as e:
                    # Network is down: [Errno 100] Network is down (Linux ENETDOWN)
                    if getattr(e, 'errno', None) == 100:
                        error(f"Network down on interface {self.__interface1}, will rebind: {e}")
                        self.__forward_receiving_socket1 = None
                        from time import sleep
                        sleep(1)
                    else:
                        error(f"Raw socket recv error: {e}")
                except Exception as e:
                    error(f"Raw socket recv error: {e}")

    def process_forward2(self):
        """
        Continuously process UDP packets received on interface2 and forward them to the output interface.
        """
        while self.__is_running:
            if (
                self.__forward_receiving_socket2 is None
                or not self.__interface_is_up(self.__interface2)
            ):
                self.__forward_receiving_socket2 = self.__rebind_socket(self.__forward_receiving_socket2, self.__interface2)
                if self.__forward_receiving_socket2 is None:
                    from time import sleep
                    sleep(1)
                    continue
            try:
                ready, _, _ = select([self.__forward_receiving_socket2], [], [], 1.0)
            except Exception as e:
                error(f"Select error on forward2: {e}")
                continue
            if ready:
                try:
                    pkt, _ = self.__forward_receiving_socket2.recvfrom(65535)
                    ip_header = pkt[14:34]
                    udp_header = pkt[34:42]
                    iph = unpack('!BBHHHBBH4s4s', ip_header)
                    protocol = iph[6]
                    if protocol != 17:
                        continue  # Not UDP
                    src_addr = inet_ntoa(iph[8])
                    dst_addr = inet_ntoa(iph[9])
                    self.__ip2 = src_addr
                    udph = unpack('!HHHH', udp_header)
                    src_port, dst_port = udph[0], udph[1]
                    if dst_port in (53, 67, 68, 5353):
                        debug(f"[SKIP] Skipping UDP packet to reserved port {dst_port}")
                        continue
                    data = pkt[42:]
                    debug(f"[RECV] UDP {src_addr}:{src_port} → {dst_addr}:{dst_port}, {len(data)} bytes")
                    try:
                        target_ip = self.__gateway_out
                        if self.__ip_out is not None:
                            target_ip = self._ip_out
                        self.__forward_sending_socket.sendto(data, (target_ip, dst_port))
                        debug(f"[SEND] Forwarded to {target_ip}:{dst_port}")
                    except Exception as e:
                        error(f"Failed to forward: {e}")
                except OSError as e:
                    if getattr(e, 'errno', None) == 100:
                        error(f"Network down on interface {self.__interface2}, will rebind: {e}")
                        self.__forward_receiving_socket2 = None
                        from time import sleep
                        sleep(1)
                    else:
                        error(f"Raw socket recv error: {e}")
                except Exception as e:
                    error(f"Raw socket recv error: {e}")

    
    def process_forward3(self):
        """
        Continuously process UDP packets received on interface3 and forward them to the output interface.
        """
        while self.__is_running:
            if (
                self.__forward_receiving_socket3 is None
                or not self.__interface_is_up(self.__interface3)
            ):
                self.__forward_receiving_socket3 = self.__rebind_socket(self.__forward_receiving_socket3, self.__interface3)
                if self.__forward_receiving_socket3 is None:
                    from time import sleep
                    sleep(1)
                    continue
            try:
                ready, _, _ = select([self.__forward_receiving_socket3], [], [], 1.0)
            except Exception as e:
                error(f"Select error on forward3: {e}")
                continue
            if ready:
                try:
                    pkt, _ = self.__forward_receiving_socket3.recvfrom(65535)
                    ip_header = pkt[14:34]
                    udp_header = pkt[34:42]
                    iph = unpack('!BBHHHBBH4s4s', ip_header)
                    protocol = iph[6]
                    if protocol != 17:
                        continue  # Not UDP
                    src_addr = inet_ntoa(iph[8])
                    dst_addr = inet_ntoa(iph[9])
                    self.__ip3 = src_addr
                    udph = unpack('!HHHH', udp_header)
                    src_port, dst_port = udph[0], udph[1]
                    if dst_port in (53, 67, 68, 5353):
                        debug(f"[SKIP] Skipping UDP packet to reserved port {dst_port}")
                        continue
                    data = pkt[42:]
                    debug(f"[RECV] UDP {src_addr}:{src_port} → {dst_addr}:{dst_port}, {len(data)} bytes")
                    try:
                        target_ip = self.__gateway_out
                        if self.__ip_out is not None:
                            target_ip = self._ip_out
                        self.__forward_sending_socket.sendto(data, (target_ip, dst_port))
                        debug(f"[SEND] Forwarded to {target_ip}:{dst_port}")
                    except Exception as e:
                        error(f"Failed to forward: {e}")
                except OSError as e:
                    if getattr(e, 'errno', None) == 100:
                        error(f"Network down on interface {self.__interface3}, will rebind: {e}")
                        self.__forward_receiving_socket3 = None
                        from time import sleep
                        sleep(1)
                    else:
                        error(f"Raw socket recv error: {e}")
                except Exception as e:
                    error(f"Raw socket recv error: {e}")

    def process_backward(self):
        """
        Continuously process UDP packets received on the output interface and forward them back to interface1 and interface2.
        """
        while self.__is_running:

            if (
                self.__backward_receiving_socket is None
                or not self.__interface_is_up(self.__interface_out)
            ):
                self.__backward_receiving_socket = self.__rebind_socket(self.__backward_receiving_socket, self.__interface_out)
                if self.__backward_receiving_socket is None:
                    from time import sleep
                    sleep(1)
                    continue

            try:
                ready, _, _ = select([self.__backward_receiving_socket], [], [], 1.0)
            except Exception as e:
                error(f"Select error on backward: {e}")
                continue
            if ready:
                try:
                    pkt, _ = self.__backward_receiving_socket.recvfrom(65535)
                    ip_header = pkt[14:34]
                    udp_header = pkt[34:42]
                    iph = unpack('!BBHHHBBH4s4s', ip_header)
                    protocol = iph[6]
                    if protocol != 17:
                        continue  # Not UDP
                    src_addr = inet_ntoa(iph[8])
                    dst_addr = inet_ntoa(iph[9])
                    udph = unpack('!HHHH', udp_header)
                    src_port, dst_port = udph[0], udph[1]
                    if dst_port in (53, 67, 68, 5353):
                        debug(f"[SKIP] Skipping UDP packet to reserved port {dst_port}")
                        continue
                    data = pkt[42:]
                    debug(f"[RECV] UDP {src_addr}:{src_port} → {dst_addr}:{dst_port}, {len(data)} bytes")
                    try:
                        target_ip1 = self.__gateway1
                        if self.__ip1 is not None:
                            target_ip1 = self.__ip1
                        self.__backward_sending_socket1.sendto(data, (target_ip1, dst_port))
                        target_ip2 = self.__gateway2
                        if self.__ip2 is not None:
                            target_ip2 = self.__ip2
                        self.__backward_sending_socket2.sendto(data, (target_ip2, dst_port))
                        target_ip3 = self.__gateway2
                        if self.__ip3 is not None:
                            target_ip3 = self.__ip3
                        self.__backward_sending_socket3.sendto(data, (target_ip3, dst_port))
                        debug(f"[SEND] Forwarded to {target_ip1}:{dst_port} , {target_ip2}:{dst_port} and {target_ip3}:{dst_port}")
                    except Exception as e:
                        error(f"Failed to forward: {e}")
                except OSError as e:
                    if getattr(e, 'errno', None) == 100:
                        error(f"Network down on interface {self.__interface_out}, will rebind: {e}")
                        self.__backward_receiving_socket = None
                        from time import sleep
                        sleep(1)
                    else:
                        error(f"Raw socket recv error: {e}")
                except Exception as e:
                    error(f"Raw socket recv error: {e}")


    def stop(self) :
        """Close all sockets and stop the forwarder."""
        if self.__backward_receiving_socket is not None : self.__backward_receiving_socket.close()
        if self.__backward_sending_socket1  is not None : self.__backward_sending_socket1.close()
        if self.__backward_sending_socket2  is not None : self.__backward_sending_socket2.close()
        if self.__backward_sending_socket3  is not None : self.__backward_sending_socket3.close()
        if self.__forward_receiving_socket1 is not None : self.__forward_receiving_socket1.close()
        if self.__forward_receiving_socket2 is not None : self.__forward_receiving_socket2.close()
        if self.__forward_receiving_socket3 is not None : self.__forward_receiving_socket3.close()
        if self.__forward_sending_socket    is not None : self.__forward_sending_socket.close()


    def __handle_signal(self, signum, frame):
        """Handle termination signals to cleanly stop the forwarder."""
        info("Signal received, exiting...")
        self.__is_running = False

    def __interface_is_up(self, interface):
        """
        Check if a network interface is up using ioctl SIOCGIFFLAGS.
        """
        try:
            s = socket(AF_INET, SOCK_DGRAM)
            ifreq = pack('256s', interface[:15].encode('utf-8'))
            flags = unpack('H', ioctl(s, 0x8913, ifreq)[16:18])[0]  # SIOCGIFFLAGS
            return flags & 1  # IFF_UP
        except Exception as e:
            error(f"Failed to check interface status for {interface}: {e}")
            return False

    def __rebind_socket(self, sock, interface):
        """
        Attempt to close and reopen a raw socket on the given interface.
        """
        try:
            if sock:
                sock.close()
        except Exception:
            pass

        result = None

        try:
            result = socket(AF_PACKET, SOCK_RAW, ntohs(0x0800))
            result.bind((interface, 0))
            result.setblocking(0)
            info(f"Rebound raw socket to {interface}")
        except Exception as e:
            error(f"Failed to rebind raw socket to {interface}: {e}")

        return result
    
        

if __name__ == "__main__":

    # Instantiate the UDP forwarder
    forwarder = UdpForwarder()

    # Command-line interface to specify source/destination IPs and interfaces
    parser = ArgumentParser(description="UDP forwarder for Limelight discovery")
    parser.add_argument("--from-ip1", dest="src_ip1", required=True, help="Source IP to listen on")
    parser.add_argument("--from-ip2", dest="src_ip2", required=True, help="Source IP to listen on")
    parser.add_argument("--from-ip3", dest="src_ip3", required=True, help="Source IP to listen on")
    parser.add_argument("--to-ip", dest="dst_ip", required=True, help="Destination IP to forward to")
    parser.add_argument("--from-interface1", dest="src_int1", required=True, help="Interface for reverse direction")
    parser.add_argument("--from-interface2", dest="src_int2", required=True, help="Interface for reverse direction")
    parser.add_argument("--from-interface3", dest="src_int3", required=True, help="Interface for reverse direction")
    parser.add_argument("--to-interface", dest="dst_int", required=True, help="Interface for forward direction")

    args = parser.parse_args()

    # Configure and start the forwarder
    forwarder.configure(args.src_ip1, args.src_ip2, args.src_ip3 , args.dst_ip, args.src_int1, args.src_int2, args.src_int3, args.dst_int, 5809)
    
    started = False
    while not started :  started = forwarder.start()


    # Launch threads to handle forwarding in both directions concurrently
    threads = []
    threads.append(Thread(target=forwarder.process_forward1, args=(), daemon=True))
    threads.append(Thread(target=forwarder.process_forward2, args=(), daemon=True))
    threads.append(Thread(target=forwarder.process_forward3, args=(), daemon=True))
    threads.append(Thread(target=forwarder.process_backward, args=(), daemon=True))

    for t in threads:
        t.start()

    info("UDP forwarder running. Press Ctrl+C to stop.")
    
    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        info("Exiting.")

    forwarder.stop()
