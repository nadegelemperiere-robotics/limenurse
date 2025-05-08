#! /bin/bash
# -------------------------------------------------------
# Copyright (c) [2025] Nadege Lemperiere
# All rights reserved
# -------------------------------------------------------
# Create project documentation
# -------------------------------------------------------
# Nadège LEMPERIERE, @5th May 2025
# Latest revision: 5th May 2025
# -------------------------------------------------------

# Retrieve absolute path to this script
script=$(readlink -f $0)
scriptpath=`dirname $script`

# Create virtual environment
python3 -m venv /tmp/generate-doc
. /tmp/generate-doc/bin/activate

# Install required python packages
pip install --quiet sphinx
pip install --quiet sphinx-rtd-theme

# Launch generation
sphinx-build -b html $scriptpath/../docs $scriptpath/../docs/_build/html

# Deactivate virtual environment
deactivate
rm -Rf /tmp/generate-doc/

