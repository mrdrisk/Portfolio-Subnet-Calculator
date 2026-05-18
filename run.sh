#!/usr/bin/env bash
# run.sh — subnet calculator launcher
#
# Usage:
#   ./run.sh 192.168.1.0/24          # run a calculation
#   ./run.sh --history                # show history
#   ./run.sh --serve                  # start the frontend dev server
#   ./run.sh --serve 9090             # start on a custom port
 
set -euo pipefail
 
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLI_DIR="$SCRIPT_DIR/cli"
FRONTEND_DIR="$SCRIPT_DIR/frontend"
 
usage() {
  echo "Usage:"
  echo "  ./run.sh <CIDR>           Run a subnet calculation"
  echo "  ./run.sh --history        Show calculation history"
  echo "  ./run.sh --serve [port]   Start the frontend on localhost (default: 8000)"
  echo ""
  echo "Examples:"
  echo "  ./run.sh 10.0.0.0/8"
  echo "  ./run.sh 192.168.1.0/24 --no-history"
  echo "  ./run.sh --serve 8080"
}
 
if [[ $# -eq 0 ]]; then
  usage
  exit 0
fi
 
case "$1" in
  --serve)
    PORT="${2:-8000}"
    echo "Serving frontend at http://localhost:$PORT"
    python3 -m http.server "$PORT" --directory "$FRONTEND_DIR"
    ;;
  --help|-h)
    usage
    ;;
  *)
    # Pass all arguments through to the Python CLI
    python3 "$CLI_DIR/subnet_calc.py" "$@"
    ;;
esac
