from __future__ import annotations

import os
import plistlib
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Sequence


APP_NAME = "Julian Today"
LAUNCH_AGENT_LABEL = "com.juliantoday.tray"


class StartupError(RuntimeError):
    pass


def is_startup_supported() -> bool:
    return platform.system() in {"Windows", "Darwin"}


def is_startup_enabled() -> bool:
    system = platform.system()
    if system == "Windows":
        return windows_shortcut_path().exists()
    if system == "Darwin":
        return macos_launch_agent_path().exists()
    return False


def add_to_startup() -> Path:
    system = platform.system()
    if system == "Windows":
        return add_windows_startup()
    if system == "Darwin":
        return add_macos_startup()
    raise StartupError(f"Startup is not supported on {system}.")


def remove_from_startup() -> Path:
    system = platform.system()
    if system == "Windows":
        path = windows_shortcut_path()
        path.unlink(missing_ok=True)
        return path
    if system == "Darwin":
        path = macos_launch_agent_path()
        if path.exists():
            subprocess.run(["launchctl", "unload", str(path)], check=False)
            path.unlink()
        return path
    raise StartupError(f"Startup is not supported on {system}.")


def current_app_command() -> Sequence[str]:
    executable = Path(sys.executable).resolve()

    if getattr(sys, "frozen", False):
        return [str(executable)]

    return [str(executable), str(Path(__file__).with_name("julian_tray.py").resolve())]


def add_windows_startup() -> Path:
    shortcut = windows_shortcut_path()
    shortcut.parent.mkdir(parents=True, exist_ok=True)
    command = current_app_command()
    target = command[0]
    arguments = subprocess.list2cmdline(command[1:])
    working_directory = str(Path(target).parent)

    script = f"""
$ShortcutPath = {powershell_literal(str(shortcut))}
$TargetPath = {powershell_literal(target)}
$Arguments = {powershell_literal(arguments)}
$WorkingDirectory = {powershell_literal(working_directory)}
$Shell = New-Object -ComObject WScript.Shell
$Shortcut = $Shell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $TargetPath
$Shortcut.Arguments = $Arguments
$Shortcut.WorkingDirectory = $WorkingDirectory
$Shortcut.Save()
"""
    subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            script,
        ],
        check=True,
    )
    return shortcut


def powershell_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def add_macos_startup() -> Path:
    path = macos_launch_agent_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    plist = {
        "Label": LAUNCH_AGENT_LABEL,
        "ProgramArguments": list(current_app_command()),
        "RunAtLoad": True,
        "KeepAlive": False,
        "ProcessType": "Interactive",
    }
    with path.open("wb") as plist_file:
        plistlib.dump(plist, plist_file)

    launchctl = shutil.which("launchctl")
    if launchctl is not None:
        subprocess.run([launchctl, "unload", str(path)], check=False)
        subprocess.run([launchctl, "load", str(path)], check=False)
    return path


def windows_shortcut_path() -> Path:
    startup_dir = os.environ.get("APPDATA")
    if not startup_dir:
        raise StartupError("APPDATA is not set; cannot locate the Startup folder.")
    return (
        Path(startup_dir)
        / "Microsoft"
        / "Windows"
        / "Start Menu"
        / "Programs"
        / "Startup"
        / "JulianToday.lnk"
    )


def macos_launch_agent_path() -> Path:
    return Path.home() / "Library" / "LaunchAgents" / f"{LAUNCH_AGENT_LABEL}.plist"
