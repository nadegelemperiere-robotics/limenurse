#!/bin/bash
# -------------------------------------------------------
# Copyright (c) [2024] FASNY
# All rights reserved
# -------------------------------------------------------
# Script installing and executing registration
# -------------------------------------------------------
# Nadège LEMPERIERE, @6th september 2024
# Latest revision: 6th september 2024
# -------------------------------------------------------

# Retrieve absolute path to this script
script=$(readlink -f $0)
scriptpath=`dirname $script`

# Create virtual environment
python3 -m venv /tmp/configure-route
. /tmp/configure-route/bin/activate

# Install required python packages
pip install --quiet -r $scriptpath/../requirements-test.txt

# Launch tests
python3 $scriptpath/../tests/routing_tester.py run $@

# Deactivate virtual environment
deactivate
rm -Rf /tmp/configure-route/

