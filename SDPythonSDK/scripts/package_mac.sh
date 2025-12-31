#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SDK_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PLUGIN_ID="com.mirabox.streamdock.goveelightcontrol.sdPlugin"
PLUGIN_SRC="${SDK_ROOT}/${PLUGIN_ID}"

VENV_PY="${VENV_PY:-${SDK_ROOT}/venv/bin/python}"
if [ ! -x "${VENV_PY}" ]; then
  echo "Missing venv python at ${VENV_PY}" >&2
  echo "Create it with: /opt/homebrew/bin/python3 -m venv \"${SDK_ROOT}/venv\"" >&2
  exit 1
fi

if ! "${VENV_PY}" -m PyInstaller --version >/dev/null 2>&1; then
  echo "PyInstaller not found in venv. Install with:" >&2
  echo "  \"${VENV_PY}\" -m pip install pyinstaller" >&2
  exit 1
fi

PYI_DIST="${SDK_ROOT}/build/pyinstaller/dist"
PYI_BUILD="${SDK_ROOT}/build/pyinstaller/build"
mkdir -p "${PYI_DIST}" "${PYI_BUILD}"

echo "Building macOS binary..."
"${VENV_PY}" -m PyInstaller "${SDK_ROOT}/main.spec" \
  --noconfirm \
  --distpath "${PYI_DIST}" \
  --workpath "${PYI_BUILD}"

BIN_PATH="${PYI_DIST}/GoveeLightControl"
if [ ! -f "${BIN_PATH}" ]; then
  echo "Expected binary not found at ${BIN_PATH}" >&2
  exit 1
fi

DIST_ROOT="${SDK_ROOT}/dist"
DIST_BUNDLE="${DIST_ROOT}/${PLUGIN_ID}"
rm -rf "${DIST_BUNDLE}"
mkdir -p "${DIST_ROOT}"
cp -R "${PLUGIN_SRC}" "${DIST_BUNDLE}"

DIST_BUNDLE="${DIST_BUNDLE}" python3 - <<'PY'
import json
import os

bundle = os.environ["DIST_BUNDLE"]
manifest_path = os.path.join(bundle, "manifest.json")
with open(manifest_path, "r", encoding="utf-8") as f:
    data = json.load(f)
data["CodePath"] = "GoveeLightControl"
data["CodePathMac"] = "GoveeLightControl"
with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=True, indent=2)
PY

rm -f "${DIST_BUNDLE}/plugin_mac.sh"
cp "${BIN_PATH}" "${DIST_BUNDLE}/GoveeLightControl"

ZIP_PATH="${DIST_ROOT}/${PLUGIN_ID}.zip"
rm -f "${ZIP_PATH}"
(cd "${DIST_ROOT}" && /usr/bin/zip -r "${PLUGIN_ID}.zip" "${PLUGIN_ID}" >/dev/null)
echo "Zip ready: ${ZIP_PATH}"

echo "Bundle ready: ${DIST_BUNDLE}"
