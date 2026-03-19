param(
    [string]$Python = "python",
    [switch]$RemovePackage
)

$ErrorActionPreference = "Stop"
$pythonPath = (Get-Command $Python -ErrorAction Stop).Source

Write-Host "Removing Codex integration assets..."
& $pythonPath -m codex_observatory uninstall-codex

if ($RemovePackage) {
    Write-Host "Removing codex-observatory package..."
    & $pythonPath -m pip uninstall -y codex-observatory
}

Write-Host ""
Write-Host "Done."
