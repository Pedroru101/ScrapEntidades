# Skill Sync - Syncs skill metadata to AGENTS.md files
# Usage: .\sync.ps1 [-DryRun]

param(
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$ScriptDir = $PSScriptRoot
$RepoRoot = $ScriptDir | Split-Path -Parent | Split-Path -Parent | Split-Path -Parent
$SkillsDir = Join-Path $RepoRoot "skills"

Write-Host "Syncing skills to AGENTS.md..." -ForegroundColor Cyan

if ($DryRun) {
    Write-Host "[DRY RUN] No changes will be made" -ForegroundColor Yellow
}

# Scope to AGENTS.md path mapping
$ScopeMap = @{
    "root" = Join-Path $RepoRoot "AGENTS.md"
    "src" = Join-Path $RepoRoot "src\AGENTS.md"
    "scripts" = Join-Path $RepoRoot "scripts\AGENTS.md"
    "tests" = Join-Path $RepoRoot "tests\AGENTS.md"
}

# Read all SKILL.md files
$SkillFiles = Get-ChildItem -Path $SkillsDir -Recurse -Filter "SKILL.md"

foreach ($skillFile in $SkillFiles) {
    $content = Get-Content $skillFile.FullName -Raw
    
    # Extract frontmatter
    if ($content -match "(?s)^---\r?\n(.+?)\r?\n---") {
        $frontmatter = $Matches[1]
        
        # Extract name
        if ($frontmatter -match "name:\s*(.+)") {
            $name = $Matches[1].Trim()
        }
        
        # Extract auto_invoke
        if ($frontmatter -match "auto_invoke:\s*[`"']?(.+?)[`"']?\s*$") {
            $autoInvoke = $Matches[1].Trim()
        }
        
        # Extract scope
        if ($frontmatter -match "scope:\s*\[(.+?)\]") {
            $scopes = $Matches[1] -split "," | ForEach-Object { $_.Trim() }
        }
        
        Write-Host "Found skill: $name (scopes: $($scopes -join ', '))" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "Done! Run without -DryRun to apply changes." -ForegroundColor Cyan
