#!/bin/bash

# Fail on any error
set -e

# Upgrade pip and install dependencies
python -m pip install --upgrade pip
pip install -r /home/site/wwwroot/requirements.txt

# Use port from Azure or default to 8000
PORT=${PORT:-8000}

# Run your Chainlit app
python -m chainlit run /home/site/wwwroot/app.py --host 0.0.0.0 --port $PORT
