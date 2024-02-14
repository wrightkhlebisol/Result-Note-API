#!/usr/bin/env bash

# Deactivate any existing virtual environment
conda deactivate && deactivate && echo "++++++++Deactivated conda and venv env $?+++++++++"

# Activate the virtual environment
source venv/bin/activate && echo "++++++++Sourced venv $?+++++++++++"

# Set appropriate environment variables
export FLASK_APP=flask_api_template.py
export FLASK_DEBUG=1
export SECRET_KEY=
export JWT_SECRET_KEY=

# Run the application
flask db upgrade && echo "+++++++++DB Upgraded.+++++++++++++++++"
flask run
