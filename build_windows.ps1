$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Venv = Join-Path $Root ".venv-build"
$Python = Join-Path $Venv "Scripts\python.exe"
$OutputExe = Join-Path $Root "dist\JulianToday.exe"

function Invoke-Checked {
    param(
        [Parameter(ValueFromRemainingArguments = $true)]
        [object[]] $Command
    )

    $Executable = $Command[0]
    $Arguments = @()
    if ($Command.Count -gt 1) {
        $Arguments = $Command[1..($Command.Count - 1)]
    }

    & $Executable @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code $LASTEXITCODE`: $Executable $Arguments"
    }
}

if (-not (Test-Path -LiteralPath $Python)) {
    Invoke-Checked python -m venv $Venv
}

Invoke-Checked $Python -m pip install --upgrade pip
Invoke-Checked $Python -m pip install -r (Join-Path $Root "requirements.txt") -r (Join-Path $Root "requirements-build.txt")

$RunningApp = Get-Process -Name "JulianToday" -ErrorAction SilentlyContinue |
    Where-Object { $_.Path -eq $OutputExe }
if ($RunningApp) {
    throw "JulianToday.exe is currently running. Quit it from the tray menu before rebuilding."
}

Invoke-Checked $Python -m PyInstaller `
    --clean `
    --noconfirm `
    --onefile `
    --windowed `
    --name "JulianToday" `
    --icon (Join-Path $Root "assets\calendar-icon.ico") `
    --add-data "$(Join-Path $Root 'assets\calendar-icon.png');assets" `
    --hidden-import "pystray._win32" `
    (Join-Path $Root "julian_tray.py")

Write-Host ""
Write-Host "Built: $OutputExe"
