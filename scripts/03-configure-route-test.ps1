# -------------------------------------------------------
# Copyright (c) [2024] FASNY
# All rights reserved
# -------------------------------------------------------
# Script installing and executing registration
# -------------------------------------------------------
# Nadège LEMPERIERE, @6th September 2024
# Latest revision: 6th September 2024
# -------------------------------------------------------

# Get the absolute path to this script
$scriptPath = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition

# Define temp venv path
$venvPath = Join-Path $env:TEMP "configure-route"

# Create virtual environment
python -m venv $venvPath

# Activate the venv
& "$venvPath\Scripts\Activate.ps1"

# Install dependencies
pip install --quiet -r "$scriptPath\..\requirements-test.txt"

# Run the network tester
python "$scriptPath\..\tests\routing_tester.py" run @args

# Deactivate and remove the venv
deactivate
Remove-Item -Recurse -Force $venvPath