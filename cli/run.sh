#!/bin/bash
# Usage: ./run.sh 192.168.1.0/24
python3 subnet_calc.py "$@"
cd frontend
python3 -m http.server 8000
