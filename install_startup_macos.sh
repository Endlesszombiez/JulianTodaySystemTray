#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_PATH="${1:-$ROOT/dist/JulianToday.app}"
LABEL="com.juliantoday.tray"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"

if [[ "$APP_PATH" == *.app ]]; then
    EXECUTABLE="$APP_PATH/Contents/MacOS/JulianToday"
else
    EXECUTABLE="$APP_PATH"
fi

if [[ ! -x "$EXECUTABLE" ]]; then
    echo "Cannot find executable: $EXECUTABLE" >&2
    exit 1
fi

xml_escape() {
    local value="$1"
    value="${value//&/&amp;}"
    value="${value//</&lt;}"
    value="${value//>/&gt;}"
    value="${value//\"/&quot;}"
    value="${value//\'/&apos;}"
    printf '%s' "$value"
}

EXECUTABLE_XML="$(xml_escape "$EXECUTABLE")"

mkdir -p "$HOME/Library/LaunchAgents"
cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>$LABEL</string>
    <key>ProgramArguments</key>
    <array>
        <string>$EXECUTABLE_XML</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
    <key>ProcessType</key>
    <string>Interactive</string>
</dict>
</plist>
EOF

launchctl bootout "gui/$(id -u)" "$PLIST" >/dev/null 2>&1 || true
launchctl bootstrap "gui/$(id -u)" "$PLIST" >/dev/null 2>&1 || true

echo "Added startup entry: $PLIST"
