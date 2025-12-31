#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
SDK_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

exec "/Users/christophergeno/GIT/StreamDock-Plugin-SDK/SDPythonSDK/venv/bin/python" "${SDK_ROOT}/main.py" "$@"
