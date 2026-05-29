param(
    [string] $AppPath = ""
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $AppPath) {
    $AppPath = Join-Path $Root "dist\JulianToday.exe"
}

$ResolvedApp = Resolve-Path -LiteralPath $AppPath -ErrorAction Stop
$StartupFolder = [Environment]::GetFolderPath("Startup")
$ShortcutPath = Join-Path $StartupFolder "JulianToday.lnk"

$Shell = New-Object -ComObject WScript.Shell
$Shortcut = $Shell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $ResolvedApp.Path
$Shortcut.WorkingDirectory = Split-Path -Parent $ResolvedApp.Path
$Shortcut.Save()

Write-Host "Added startup entry: $ShortcutPath"
