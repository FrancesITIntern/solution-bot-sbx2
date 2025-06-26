#!/bin/bash

# Upgrade pip first
python -m pip install --upgrade pip

# Install dependencies
python -m pip install -r requirements.txt

# Set port variable (default 8000)
PORT=${PORT:-8000}

# Run the Chainlit app
python -m chainlit run app.py --host 0.0.0.0 --port $PORT
