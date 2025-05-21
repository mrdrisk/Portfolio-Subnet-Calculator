#!/bin/bash
# Usage: ./run.sh 192.168.1.0/24
python3 subnet_calc.py "$@"

cd /path/to/Portfolio-Subnet-Calculator/cli
python3 subnet_calc.py 192.168.100.0/24

python3 subnet_calc.py --history