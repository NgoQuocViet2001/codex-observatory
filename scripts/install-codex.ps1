param(
    [string]$Python = "python",
    [switch]$PatchCodex
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$pythonPath = (Get-Command $Python -ErrorAction Stop).Source

Write-Host "Installing codex-observatory package..."
& $pythonPath -m pip install -e $repoRoot

Write-Host "Installing Codex integration assets..."
$integrationArgs = @(
    "-m",
    "codex_observatory.codex_integration",
    "--repo-root",
    $repoRoot,
    "--python-bin",
    $pythonPath
)
if ($PatchCodex) {
    $integrationArgs += "--patch-codex"
}
& $pythonPath @integrationArgs

Write-Host ""
Write-Host "Done."
Write-Host "Try:"
if ($PatchCodex) {
    Write-Host "  This install includes the Codex launcher patch."
    Write-Host "  codex stats"
    Write-Host "  codex stats compact"
} else {
    Write-Host "  This install adds the Codex skill and helper tools only."
    Write-Host "  It does NOT enable `codex stats` yet."
    Write-Host ""
    Write-Host "  codex-observatory"
    Write-Host "  codex-stats"
    Write-Host "  codex-stats compact"
    Write-Host ""
    Write-Host "Want a built-in style Codex subcommand?"
    Write-Host "  .\scripts\install-codex.ps1 -PatchCodex"
}
