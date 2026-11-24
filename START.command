#!/bin/bash
cd "$(dirname "$0")" || exit 1
read -r -s -p 'Choose or enter administrator password (12+ characters): ' AADI_ADMIN_PASSWORD
echo
export AADI_ADMIN_PASSWORD
open http://127.0.0.1:8080
python3 app.py
