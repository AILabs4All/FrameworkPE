#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH" python3 "$SCRIPT_DIR/pangolin/cli.py" "$@"
