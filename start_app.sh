#!/usr/bin/env bash

# Deactivate any existing virtual environment
conda deactivate && deactivate

# Activate the virtual environment
source venv/bin/activate

# Set appropriate environment variables
export FLASK_APP=flask_api_template.py
export FLASK_DEBUG=1

# Run the application
flask db upgrade
flask run