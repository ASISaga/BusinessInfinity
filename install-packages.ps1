

# install-packages.ps1: Ensures venv is activated, then delegates install process to Python orchestrator
$ErrorActionPreference = 'Stop'

# Always activate .venv from workspace root, then run orchestrator

$workspaceRoot = Split-Path -Parent $PSScriptRoot
$venvPath = Join-Path $workspaceRoot '.venv'
$activateScript = Join-Path $venvPath 'Scripts' 'Activate.ps1'
$defaultPythonExe = Join-Path $venvPath 'Scripts' 'python.exe'

if (-not (Test-Path $defaultPythonExe)) {
    Write-Error "Python venv not found at $venvPath. Please create it first."
    exit 1
}

# Determine which Python executable to use
if ($env:VIRTUAL_ENV -and (Test-Path (Join-Path $env:VIRTUAL_ENV 'Scripts' 'python.exe'))) {
    $pythonExe = Join-Path $env:VIRTUAL_ENV 'Scripts' 'python.exe'
    Write-Host "venv already activated at $env:VIRTUAL_ENV. Using $pythonExe."
} else {
    Write-Host "Activating venv at $venvPath ..."
    . $activateScript
    $pythonExe = $defaultPythonExe
}

# Delegate to Python orchestrator
$orchestrator = Join-Path $PSScriptRoot 'install' 'run_all_installs.py'
if (-not (Test-Path $orchestrator)) {
    Write-Error "Python orchestrator script not found: $orchestrator"
    exit 1
}

& $pythonExe $orchestrator
