#!/bin/bash
cd "$(dirname "$0")"
read -s -p 'Choose an admin password for this session: ' AADI_ADMIN_PASSWORD
printf '\n'
export AADI_ADMIN_PASSWORD
open http://localhost:8769
python3 server.py
