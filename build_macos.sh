#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$ROOT/.venv-build"
PYTHON="$VENV/bin/python"

if [ ! -x "$PYTHON" ]; then
    python3 -m venv "$VENV"
fi

"$PYTHON" -m pip install --upgrade pip
"$PYTHON" -m pip install -r "$ROOT/requirements.txt" -r "$ROOT/requirements-build.txt"

ICONSET="$ROOT/build/JulianToday.iconset"
mkdir -p "$ICONSET"
sips -z 16 16 "$ROOT/assets/calendar-icon.png" --out "$ICONSET/icon_16x16.png" >/dev/null
sips -z 32 32 "$ROOT/assets/calendar-icon.png" --out "$ICONSET/icon_16x16@2x.png" >/dev/null
sips -z 32 32 "$ROOT/assets/calendar-icon.png" --out "$ICONSET/icon_32x32.png" >/dev/null
sips -z 64 64 "$ROOT/assets/calendar-icon.png" --out "$ICONSET/icon_32x32@2x.png" >/dev/null
sips -z 128 128 "$ROOT/assets/calendar-icon.png" --out "$ICONSET/icon_128x128.png" >/dev/null
sips -z 256 256 "$ROOT/assets/calendar-icon.png" --out "$ICONSET/icon_128x128@2x.png" >/dev/null
sips -z 256 256 "$ROOT/assets/calendar-icon.png" --out "$ICONSET/icon_256x256.png" >/dev/null
sips -z 512 512 "$ROOT/assets/calendar-icon.png" --out "$ICONSET/icon_256x256@2x.png" >/dev/null
sips -z 512 512 "$ROOT/assets/calendar-icon.png" --out "$ICONSET/icon_512x512.png" >/dev/null
sips -z 1024 1024 "$ROOT/assets/calendar-icon.png" --out "$ICONSET/icon_512x512@2x.png" >/dev/null
iconutil -c icns "$ICONSET" -o "$ROOT/assets/calendar-icon.icns"

"$PYTHON" -m PyInstaller \
    --clean \
    --noconfirm \
    --windowed \
    --name "JulianToday" \
    --icon "$ROOT/assets/calendar-icon.icns" \
    --add-data "$ROOT/assets/calendar-icon.png:assets" \
    --hidden-import "pystray._darwin" \
    "$ROOT/julian_tray.py"

echo
echo "Built: $ROOT/dist/JulianToday.app"
