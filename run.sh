#!/bin/bash

# Set the correct Python path
PYTHON_PATH="/Library/Frameworks/Python.framework/Versions/3.12/bin/python3"
PIP_PATH="/Library/Frameworks/Python.framework/Versions/3.12/bin/pip3"

# Ensure required packages are installed
echo "Checking and installing required packages..."
$PIP_PATH install groq python-dotenv

# Run the agent
echo "Starting the agent..."
$PYTHON_PATH run_agent.py 