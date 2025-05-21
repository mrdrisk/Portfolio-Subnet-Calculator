#!/usr/bin/env bash
set -e

# Test valid subnet
out=$(python3 ../cli/subnet_calc.py 10.0.0.0/30)
echo "$out" | grep -q "Network:       10.0.0.0/30"
echo "$out" | grep -q "Broadcast:     10.0.0.3"

# Test history flag
python3 ../cli/subnet_calc.py --history | grep -q "Last"

# Test invalid
if python3 ../cli/subnet_calc.py invalid_cidr; then
  echo "ERROR: should have failed on invalid input" >&2
  exit 1
fi

echo "All CLI tests passed."

chmod +x test/test_cli.sh
./test/test_cli.sh
