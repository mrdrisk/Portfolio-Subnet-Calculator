#!/usr/bin/env bash
# test_cli.sh
# Integration tests for subnet_calc.py CLI.
# Tests actual output and exit codes — no framework needed.
#
# Usage (from repo root):
#   bash test/test_cli.sh
#
# Exit code: 0 if all tests pass, 1 if any fail.
 
set -uo pipefail
 
CLI="python3 cli/subnet_calc.py"
PASS=0
FAIL=0
ERRORS=()
 
# ── Test runner ───────────────────────────────────────────────────────────────
 
# assert_contains <test_name> <expected_string> <actual_output>
assert_contains() {
  local name="$1"
  local expected="$2"
  local actual="$3"
 
  if echo "$actual" | grep -qF "$expected"; then
    echo "  PASS  $name"
    PASS=$((PASS + 1))
  else
    echo "  FAIL  $name"
    echo "        expected to find: $expected"
    echo "        in output:        $(echo "$actual" | head -3)"
    FAIL=$((FAIL + 1))
    ERRORS+=("$name")
  fi
}
 
# assert_exit_code <test_name> <expected_code> <actual_code>
assert_exit_code() {
  local name="$1"
  local expected="$2"
  local actual="$3"
 
  if [[ "$actual" -eq "$expected" ]]; then
    echo "  PASS  $name"
    PASS=$((PASS + 1))
  else
    echo "  FAIL  $name"
    echo "        expected exit code $expected, got $actual"
    FAIL=$((FAIL + 1))
    ERRORS+=("$name")
  fi
}
 
# ── Tests ─────────────────────────────────────────────────────────────────────
 
echo ""
echo "Running CLI integration tests..."
echo ""
 
# /24 — standard subnet
OUTPUT=$($CLI 192.168.1.0/24 --no-history 2>&1)
assert_contains "/24 network address"    "192.168.1.0/24"    "$OUTPUT"
assert_contains "/24 subnet mask"        "255.255.255.0"     "$OUTPUT"
assert_contains "/24 wildcard mask"      "0.0.0.255"         "$OUTPUT"
assert_contains "/24 broadcast"          "192.168.1.255"     "$OUTPUT"
assert_contains "/24 host min"           "192.168.1.1"       "$OUTPUT"
assert_contains "/24 host max"           "192.168.1.254"     "$OUTPUT"
assert_contains "/24 usable hosts"       "254"               "$OUTPUT"
assert_contains "/24 scope private"      "Private"           "$OUTPUT"
assert_contains "/24 ip class"          "C"                  "$OUTPUT"
 
# /8 — class A
OUTPUT=$($CLI 10.0.0.0/8 --no-history 2>&1)
assert_contains "/8 network address"     "10.0.0.0/8"        "$OUTPUT"
assert_contains "/8 broadcast"           "10.255.255.255"    "$OUTPUT"
assert_contains "/8 usable hosts"        "16777214"          "$OUTPUT"
assert_contains "/8 ip class"           "A"                  "$OUTPUT"
assert_contains "/8 scope private"       "Private"           "$OUTPUT"
 
# /16
OUTPUT=$($CLI 172.16.0.0/16 --no-history 2>&1)
assert_contains "/16 network address"    "172.16.0.0/16"     "$OUTPUT"
assert_contains "/16 broadcast"          "172.16.255.255"    "$OUTPUT"
assert_contains "/16 usable hosts"       "65534"             "$OUTPUT"
 
# /30 — smallest normal subnet
OUTPUT=$($CLI 192.168.1.0/30 --no-history 2>&1)
assert_contains "/30 host min"           "192.168.1.1"       "$OUTPUT"
assert_contains "/30 host max"           "192.168.1.2"       "$OUTPUT"
assert_contains "/30 usable hosts"       "2"                 "$OUTPUT"
 
# /32 — host route
OUTPUT=$($CLI 192.168.1.1/32 --no-history 2>&1)
assert_contains "/32 usable hosts"       "1"                 "$OUTPUT"
 
# Public IP
OUTPUT=$($CLI 8.8.8.0/24 --no-history 2>&1)
assert_contains "public scope"           "Public"            "$OUTPUT"
 
# Host bits set — should still resolve to network address
OUTPUT=$($CLI 192.168.1.10/24 --no-history 2>&1)
assert_contains "host bits set -> network" "192.168.1.0/24" "$OUTPUT"
 
# ── Invalid input — should exit non-zero ──────────────────────────────────────
 
$CLI not-an-ip --no-history > /dev/null 2>&1 || EXIT=$?
assert_exit_code "invalid input exits non-zero" 1 "${EXIT:-0}"
 
$CLI 192.168.1.0 --no-history > /dev/null 2>&1 || EXIT=$?
assert_exit_code "missing prefix exits non-zero" 1 "${EXIT:-0}"
 
# ── --history flag — should not error when DB exists ─────────────────────────
 
$CLI --history > /dev/null 2>&1
assert_exit_code "--history flag exits cleanly" 0 "$?"
 
# ── Summary ───────────────────────────────────────────────────────────────────
 
echo ""
echo "────────────────────────────────"
echo "  Results: $PASS passed, $FAIL failed"
 
if [[ $FAIL -gt 0 ]]; then
  echo ""
  echo "  Failed tests:"
  for err in "${ERRORS[@]}"; do
    echo "    - $err"
  done
  echo ""
  exit 1
fi
 
echo "  All tests passed."
echo ""
exit 0
