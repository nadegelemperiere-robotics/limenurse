# -------------------------------------------------------
# Copyright (c) [2025] Nadege Lemperiere
# All rights reserved
# -------------------------------------------------------
"""
Script to test the USB gadget configuration of a Limelight device
as detected externally from a user's perspective.
This includes validating device presence, parsing USB descriptors,
and comparing them against a known reference.
"""
# -------------------------------------------------------
# Nadège LEMPERIERE, @30th April 2025
# Latest revision: 30th April 2025
# -------------------------------------------------------

# System includes
from logging                        import getLogger
from os                             import path
from subprocess                     import check_output, CalledProcessError, DEVNULL
from json                           import load
from re                             import search

# Logger configuration settings
logg_conf_path = path.normpath(path.join(path.dirname(__file__), '../conf/logging.conf'))
env_path = path.normpath(path.join(path.dirname(__file__), '../conf/env'))
limelight_descriptors_path = path.normpath(path.join(path.dirname(__file__), '../data/limelight-gadget.json'))

class GadgetOutsideTester:
    """
    GadgetOutsideTester performs validation of a connected Limelight device
    using lsusb. It ensures that the descriptors match a known reference,
    accounting for allowed differences such as MAC address and bus IDs.
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

    def configure(self) :
        """
        Configure the test environment by loading device reference descriptors and IP settings.

        This method reads a reference descriptor JSON and a configuration environment
        file to prepare the gadget test. This includes fetching the expected USB
        descriptors and the expected USB network IP gateway for comparison.
        """
        self.__logger.info('CONFIGURING OUTSIDE GADGET TEST')

        self.__is_ready = False

        # Load the reference limelight gadget descriptors from JSON file
        self.__limelight_reference = {}
        with open(limelight_descriptors_path, "r") as f:
            self.__limelight_reference = load(f)

        # Extract the USB IP gateway from environment configuration file
        self.__reference_ip = ""
        with open(env_path, 'r') as file:
            match = search(r'USB_IP_GATEWAY=([\d\.]+)', file.read())
            if match : 
                self.__reference_ip = match.group(1)
                
        # Mark as ready if both reference descriptors and IP are loaded
        if len(self.__limelight_reference) != 0 and len(self.__reference_ip) != 0:
            self.__is_ready = True

    def run(self) :
        """
        Validate the currently connected Limelight USB gadget by locating it via
        lsusb and comparing its descriptors to a reference snapshot.
        Known differences like MAC addresses are tolerated.

        Returns:
            bool: True if the device matches the reference descriptors (allowing known differences),
                  False otherwise.
        """
        result = False

        if self.__is_ready : 
            self.__logger.info('RUNNING OUTSIDE TESTS')
            result = True

            # find our device by vendor and product ID
            device = GadgetOutsideTester.find_device(GadgetOutsideTester.sLimelightVendor, GadgetOutsideTester.sLimelightProduct)
            if device is None:
                self.__logger.error('--> Limelight like device not found')
                result = False

            else :
                self.__logger.info('--> Limelight like device found')
                # get the USB descriptors of the device
                descriptors = GadgetOutsideTester.get_device_descriptors(GadgetOutsideTester.sLimelightVendor, GadgetOutsideTester.sLimelightProduct)
                if descriptors is None:
                    self.__logger.error('--> Could not get limelight descriptors')
                    result = False
                
                else :
                    self.__logger.info('--> Usb descriptors found')
                    
                    # Compare the reference descriptors with the actual device descriptors
                    differences = GadgetOutsideTester.deep_compare_dicts(self.__limelight_reference, descriptors)
                    for difference in differences :
                        # Allow known differences such as MAC address and bus device info
                        if difference['reason'] == 'value' and difference['path'] == 'Device Descriptor/Configuration Descriptor[1]/Interface Descriptor[0]/CDC Ethernet/iMacAddress' :
                            self.__logger.info("----> Difference in MacAdddress is allowed")
                        elif difference['reason'] == 'key' and difference['value'].startswith("Bus") :
                            self.__logger.info("----> Difference in bus device is allowed")
                        else :
                            # Log unexpected differences as errors
                            if difference['reason'] == 'key' :
                                self.__logger.error("----> Could not find key " + difference['value'] + " in one of the devices")
                            elif difference['reason'] == 'length' :
                                self.__logger.error("----> Key " + difference['path'] + " have different lengths : " + difference['1'] + " and " + difference['2'])
                            elif difference['reason'] == 'value' :
                                self.__logger.error("----> Mismatch value for path " + difference['path'] + " : " + difference['1'] + " and " + difference['2'])
                            result = False

        return result

    def find_device(vendor_id, product_id):
        """
        Find the connected USB device matching the given vendor and product IDs.

        Args:
            vendor_id (str): USB vendor ID to search for.
            product_id (str): USB product ID to search for.

        Returns:
            str or None: The lsusb line describing the device if found, otherwise None.
        """
        lines = []
        try:
            output = check_output(["lsusb"], text=True,)
            lines = output.strip().splitlines()
        except CalledProcessError:
            lines = []

        target = f"{vendor_id}:{product_id}".lower()
        for line in lines:
            if target in line.lower():
                return line.strip()
        return None

    def get_device_descriptors(vendor_id, product_id):
        """
        Retrieve the USB descriptors for the device identified by vendor and product IDs.

        Args:
            vendor_id (str): USB vendor ID.
            product_id (str): USB product ID.

        Returns:
            dict: Parsed descriptor information as a nested dictionary.
        """
        try:
            output = check_output(
                ["sudo","lsusb", "-v", "-d", f"{vendor_id}:{product_id}"],
                text=True,
                stderr=DEVNULL  # suppress "cannot open" warnings
            )
        except CalledProcessError:
            return {}

        # Parse the raw descriptor output into structured dictionary
        return GadgetOutsideTester.parse_descriptor(output)


    def parse_descriptor(output):
        """
        Parse the verbose lsusb output into a nested dictionary structure.

        Args:
            output (str): Raw output string from 'lsusb -v' command.

        Returns:
            dict: Nested dictionary representing USB descriptors.

        Supports recursive nesting and repeated keys by using a stack-based parser.
        """
        lines = output.splitlines()
    
        root = {}
        stack = [(0, root)]  # (indent level, context dict)

        for line in lines:
            stripped = line.rstrip()
            if not stripped:
                continue

            indent = len(line) - len(line.lstrip())
            # Pop stack until matching indent level is found
            while stack and indent < stack[-1][0]:
                stack.pop()

            current_context = stack[-1][1]

            if ':' in stripped:
                key, rest = stripped.split(':', 1)
                key = key.strip()
                value = rest.strip()
                if value:
                    # Insert key-value pair in current context
                    GadgetOutsideTester.insert_entry(current_context, key, value)
                else:
                    # New sub-dictionary (e.g. "Interface Descriptor:")
                    new_dict = {}
                    GadgetOutsideTester.insert_entry(current_context, key, new_dict)
                    # Increase indent level for nested context
                    stack.append((indent + 1, new_dict))
            else:
                # Line without colon
                if ' ' in stripped:
                    key, value = stripped.split(None, 1)
                    GadgetOutsideTester.insert_entry(current_context, key.strip(), value.strip())
                else:
                    GadgetOutsideTester.insert_entry(current_context, stripped, "")

        return root
    
    def insert_entry(context, key, value):
        """
        Insert a key-value pair into the given dictionary context.
        If the key already exists, convert to a list to hold multiple values.

        Args:
            context (dict): Dictionary where the entry is inserted.
            key (str): Key name.
            value: Value to insert.
        """
        if key in context:
            if isinstance(context[key], list):
                context[key].append(value)
            else:
                context[key] = [context[key], value]
        else:
            context[key] = value

    def deep_compare_dicts(d1, d2, path=""):
        """
        Recursively compare two nested dictionaries or lists and record differences.

        Args:
            d1: First dictionary or list to compare.
            d2: Second dictionary or list to compare.
            path (str): Current path in the nested structure for reporting.

        Returns:
            list: List of dictionaries describing differences found.

        Handles nested dictionaries and lists; reports missing keys, value mismatches, and length mismatches.
        Returns a list of differences, each annotated with the path and reason.
        """
        result = []

        if isinstance(d1, dict) and isinstance(d2, dict):
            keys1 = set(d1.keys())
            keys2 = set(d2.keys())
            all_keys = keys1.union(keys2)

            for key in all_keys:
                new_path = f"{path}/{key}" if path else key
                if key not in d1:
                    result.append({ "reason" : "key", "missing" : "1", "value" : new_path})
                elif key not in d2:
                    result.append({ "reason" : "key", "missing" : "2", "value" : new_path})
                else:
                    current = GadgetOutsideTester.deep_compare_dicts(d1[key], d2[key], new_path)
                    result = result + current
        
        elif isinstance(d1, list) and isinstance(d2, list):
            if len(d1) != len(d2):
                result.append(result.append({ "reason" : "length", "path" : path, "1" : len(d1), "2" : len(d2)}))
            else:
                for i, (item1, item2) in enumerate(zip(d1, d2)):
                    current = GadgetOutsideTester.deep_compare_dicts(item1, item2, f"{path}[{i}]")
                    result = result + current
        else:
            if d1 != d2:
                result.append({ "reason" : "value", "path" : path, "1" : d1, "2" : d2})
            

        return result
