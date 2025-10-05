pytest ../tests

# PowerShell script to activate venv, set PYTHONPATH, and run all test files sequentially
$workspaceRoot = Resolve-Path "$PSScriptRoot/../.."
Set-Location $workspaceRoot
& .\.venv\Scripts\Activate.ps1
Set-Location "$workspaceRoot\BusinessInfinity\tests"
$env:PYTHONPATH = "$workspaceRoot\BusinessInfinity\src"
$testFiles = @(
	"test_audit_trail.py"
	"test_consolidated_system.py"
	"test_conversations.py"
	"test_covenant_expansion.py"
	"test_enhanced_conversations.py"
	"test_enhanced_self_learning.py"
	"test_lora_adapters.py"
	"test_mcp_access_control.py"
	"test_minimal_structure.py"
	"test_network.py"
	"test_package_structure.py"
	"test_trust_compliance.py"
	"test_ultra_minimal.py"
)
foreach ($file in $testFiles) {
	if (Test-Path $file) {
		Write-Host "Running $file"
		pytest $file
		if ($LASTEXITCODE -ne 0) {
			Write-Host "Test failed: $file"
			exit $LASTEXITCODE
		}
	} else {
		Write-Host "File not found: $file"
	}
}
Write-Host "All tests completed."

# Check if venv is activated, if not, activate it
$workspaceRoot = Resolve-Path "$PSScriptRoot/../.."
if (-not $env:VIRTUAL_ENV) {
	Set-Location $workspaceRoot
	& .\.venv\Scripts\Activate.ps1
}
Set-Location "$workspaceRoot\BusinessInfinity"
$testFiles = @(
	"test_audit_trail.py"
	"test_consolidated_system.py"
	"test_conversations.py"
	"test_covenant_expansion.py"
	"test_enhanced_conversations.py"
	"test_enhanced_self_learning.py"
	"test_lora_adapters.py"
	"test_mcp_access_control.py"
	"test_minimal_structure.py"
	"test_network.py"
	"test_package_structure.py"
	"test_trust_compliance.py"
	"test_ultra_minimal.py"
)
foreach ($file in $testFiles) {
	$testPath = "tests/$file"
	if (Test-Path $testPath) {
		Write-Host "Running $testPath"
		pytest --import-mode=importlib $testPath
		if ($LASTEXITCODE -ne 0) {
			Write-Host "Test failed: $testPath"
			exit $LASTEXITCODE
		}
	} else {
		Write-Host "File not found: $testPath"
	}
}
Write-Host "All tests completed."
