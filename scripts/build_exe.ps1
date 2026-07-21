param(
    [string]$Python = ""
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

if (-not $Python) {
    if (Test-Path ".\.venv\Scripts\python.exe") {
        $Python = ".\.venv\Scripts\python.exe"
    }
    else {
        $Python = "python"
    }
}

& $Python -c "import sys; print(sys.executable)" | Out-Null

$pythonPaths = @("$ProjectRoot\src")

$buildTools = Resolve-Path ".\.build_tools" -ErrorAction SilentlyContinue
if ($buildTools) {
    $pythonPaths = @($buildTools.Path) + $pythonPaths
}

$sitePackages = Resolve-Path ".\.venv\Lib\site-packages" -ErrorAction SilentlyContinue
if ($sitePackages) {
    $pythonPaths = @($sitePackages.Path) + $pythonPaths
}

if ($env:PYTHONPATH) {
    $pythonPaths += $env:PYTHONPATH
}

$env:PYTHONPATH = $pythonPaths -join ";"

$iconPath = Join-Path $ProjectRoot "assets\icons\app.ico"
if (-not (Test-Path $iconPath)) {
    & $Python -c "import sys; from pathlib import Path; from PySide6.QtWidgets import QApplication; from PySide6.QtGui import QIcon; app = QApplication.instance() or QApplication([]); svg = Path('assets/icons/app.svg'); ico = Path('assets/icons/app.ico'); ok = QIcon(str(svg)).pixmap(256, 256).save(str(ico), 'ICO'); sys.exit(0 if ok else 1)"
}

& $Python -m PyInstaller --clean --noconfirm NexusBrowser.spec

Write-Host "Built Nexus Browser at: $ProjectRoot\dist\NexusBrowser\NexusBrowser.exe"
