# Setup AI Skills for Antigravity
# Run from project root

$ErrorActionPreference = "Stop"
$RepoRoot = $PSScriptRoot | Split-Path -Parent
$SkillsDir = $PSScriptRoot

Write-Host "Setting up AI Skills for Antigravity..." -ForegroundColor Cyan

# Create .gemini directory and symlink
$GeminiDir = Join-Path $RepoRoot ".gemini"
if (-not (Test-Path $GeminiDir)) {
    New-Item -ItemType Directory -Path $GeminiDir -Force | Out-Null
}

$SkillsLink = Join-Path $GeminiDir "skills"
if (Test-Path $SkillsLink) {
    Remove-Item $SkillsLink -Force
}

# Create symbolic link (requires admin or developer mode)
try {
    New-Item -ItemType SymbolicLink -Path $SkillsLink -Target $SkillsDir -Force | Out-Null
    Write-Host "[OK] Created symlink: .gemini/skills -> skills/" -ForegroundColor Green
} catch {
    Write-Host "[WARN] Symlink failed (need admin). Copying instead..." -ForegroundColor Yellow
    Copy-Item -Path $SkillsDir -Destination $SkillsLink -Recurse -Force
}

# Copy AGENTS.md for Gemini naming convention
$AgentsMdFiles = Get-ChildItem -Path $RepoRoot -Recurse -Filter "AGENTS.md" | Where-Object { $_.FullName -notlike "*node_modules*" }

foreach ($file in $AgentsMdFiles) {
    $dir = $file.DirectoryName
    $geminiMd = Join-Path $dir "GEMINI.md"
    Copy-Item -Path $file.FullName -Destination $geminiMd -Force
    Write-Host "[OK] Copied: $($file.Name) -> GEMINI.md" -ForegroundColor Green
}

Write-Host ""
Write-Host "Done! Restart Antigravity to load skills." -ForegroundColor Cyan
