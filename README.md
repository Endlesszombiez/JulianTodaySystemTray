# Julian Today System Tray

A small Python tray app for Windows and macOS that displays today's Julian date as `YYYY-DDD`.
The app uses `assets/calendar-icon.png` for the tray icon and packaged application icon.

## Install

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

On macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Run

```bash
python julian_tray.py
```

Right-click the tray icon to copy the date or quit. The tray value refreshes automatically at local midnight.
The right-click menu also includes startup controls.

To print the current value without starting the tray:

```bash
python julian_tray.py --print
```

## Build a self-contained app

End users do not need Python if you ship the PyInstaller output. The build machine does need Python.

Windows:

```powershell
.\build_windows.ps1
```

This creates:

```text
dist\JulianToday.exe
```

The Windows build embeds icon and Details-tab metadata from `assets/calendar-icon.ico` and `version_info.txt`.

macOS:

```bash
chmod +x ./build_macos.sh
./build_macos.sh
```

This creates:

```text
dist/JulianToday.app
```

Builds are platform-specific: create the Windows `.exe` on Windows and the macOS `.app` on macOS.

## Start at login

From the tray menu, choose **Add to Startup**.

You can also manage startup from the command line:

```bash
python install_startup.py add
python install_startup.py status
python install_startup.py remove
```

For machines without Python, use the native installer scripts after building.

Windows:

```powershell
.\install_startup_windows.ps1
.\uninstall_startup_windows.ps1
```

macOS:

```bash
chmod +x ./install_startup_macos.sh ./uninstall_startup_macos.sh
./install_startup_macos.sh
./uninstall_startup_macos.sh
```

Windows uses a shortcut in the current user's Startup folder:

```text
%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\JulianToday.lnk
```

macOS uses a LaunchAgent:

```text
~/Library/LaunchAgents/com.juliantoday.tray.plist
```
