param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }
$skillSource = Join-Path $repoRoot "integrations\codex-skill\SKILL.md"
$skillDir = Join-Path $codexHome "skills\codex-observatory"

Write-Host "Installing codex-observatory package..."
& $Python -m pip install -e $repoRoot

Write-Host "Installing Codex skill into $skillDir ..."
New-Item -ItemType Directory -Force -Path $skillDir | Out-Null
Copy-Item -Path $skillSource -Destination (Join-Path $skillDir "SKILL.md") -Force

Write-Host ""
Write-Host "Done."
Write-Host "Try:"
Write-Host "  codex-stats"
Write-Host "  codex-stats compact"
