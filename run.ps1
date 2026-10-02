# Wrapper for the wiki tooling (contract C6). Run from the repository root.
#
#   ./run.ps1 index [--check] [--root PATH]
#   ./run.ps1 lint [--root PATH]
#   ./run.ps1 serve
#   ./run.ps1 test
#
# Extra arguments pass through unchanged. Requires uv; there is no fallback
# to a system Python.

[CmdletBinding(PositionalBinding = $false)]
param(
    [Parameter(Position = 0)]
    [string]$Command,

    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Rest = @()
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Output "uv not found"
    exit 2
}

Set-Location -LiteralPath $PSScriptRoot

switch ($Command) {
    "index" { & uv run python scripts/wiki/build_index.py @Rest }
    "lint"  { & uv run python scripts/wiki/lint.py @Rest }
    "serve" { & uv run mkdocs serve @Rest }
    "test"  { & uv run pytest @Rest }
    default {
        Write-Output "usage: ./run.ps1 <index|lint|serve|test> [args...]"
        exit 2
    }
}

exit $LASTEXITCODE
