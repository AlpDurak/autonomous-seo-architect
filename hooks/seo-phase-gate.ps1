param(
  [Parameter(Position = 0)]
  [ValidateSet("init-state", "pre-phase2", "pre-edit", "pre-shell", "pre-complete")]
  [string]$Event = "pre-edit",

  [string]$Target = "",
  [string]$Tool = ""
)

$ErrorActionPreference = "Stop"
$PackageRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$Guard = Join-Path $PackageRoot "scripts\seo_state_guard.py"

$WorkspaceInput = $env:SEO_AGENT_WORKSPACE
if (-not $WorkspaceInput) {
  $WorkspaceInput = $env:CLAUDE_PROJECT_DIR
}
if (-not $WorkspaceInput) {
  $WorkspaceInput = (Get-Location).Path
}

$Workspace = Resolve-Path $WorkspaceInput

$Python = "python"
$Payload = [Console]::In.ReadToEnd()
$Args = @($Guard, $Event, "--workspace", $Workspace.Path, "--json")

if ($Target) {
  $Args += @("--target", $Target)
}

if ($Tool) {
  $Args += @("--tool", $Tool)
}

if ($Payload -and $Payload.Trim().Length -gt 0) {
  $Payload | & $Python @Args
} else {
  & $Python @Args
}

exit $LASTEXITCODE
