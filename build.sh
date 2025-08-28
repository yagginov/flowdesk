#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Clear old collected static files
rm -rf staticfiles/

# Collect static files
python manage.py collectstatic

# Apply any outstanding database migrations
python manage.py migrate
