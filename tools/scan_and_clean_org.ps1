$ORG = "automacoescomerciaisintegradas"
$WORK_DIR = "C:\antigravity\_org_scan_tmp"
$LOG_FILE = "$WORK_DIR\scan_report.txt"

$SECRETS = @(
    "AIzaSyCNdYllqEiMXRrDY3AqURxKlgCleyd_X7Q==>GEMINI_API_KEY_REMOVED",
    "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==>OPENROUTER_API_KEY_REMOVED",
    "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==>OPENAI_API_KEY_REMOVED"
)

$SECRET_VALUES = $SECRETS | ForEach-Object { ($_ -split "==>")[0] }

if (-not (Test-Path $WORK_DIR)) { New-Item -ItemType Directory -Path $WORK_DIR | Out-Null }

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
"=== Scan started: $timestamp ===" | Tee-Object -FilePath $LOG_FILE
"Org: $ORG" | Tee-Object -FilePath $LOG_FILE -Append
"" | Add-Content $LOG_FILE

Write-Host "[*] Listing repos of $ORG..." -ForegroundColor Cyan
$repos = gh repo list $ORG --limit 200 --json name,url,defaultBranchRef | ConvertFrom-Json
Write-Host "[*] Total repos: $($repos.Count)" -ForegroundColor Cyan
"Total repos: $($repos.Count)" | Add-Content $LOG_FILE

$contaminated = [System.Collections.ArrayList]@()
$clean = [System.Collections.ArrayList]@()
$errors = [System.Collections.ArrayList]@()

foreach ($repo in $repos) {
    $name = $repo.name
    $url = $repo.url
    $branch = if ($repo.defaultBranchRef) { $repo.defaultBranchRef.name } else { "main" }
    $repoPath = "$WORK_DIR\$name"

    Write-Host "`n[->] $name" -ForegroundColor Yellow

    if (Test-Path $repoPath) { Remove-Item $repoPath -Recurse -Force }

    $cloneOut = git clone --quiet "$url.git" $repoPath 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "    [ERROR] Clone failed" -ForegroundColor Red
        "ERROR | $name | Clone failed: $cloneOut" | Add-Content $LOG_FILE
        [void]$errors.Add($name)
        continue
    }

    $found = $false
    foreach ($secret in $SECRET_VALUES) {
        $logOut = git -C $repoPath log -p --all 2>&1
        if ($logOut -match [regex]::Escape($secret)) {
            $found = $true
            Write-Host "    [!!!] CONTAMINATED - secret found in history!" -ForegroundColor Red
            "[CONTAMINATED] $name - key: $($secret.Substring(0,12))..." | Add-Content $LOG_FILE
            break
        }
    }

    if (-not $found) {
        Write-Host "    [OK] Clean" -ForegroundColor Green
        "[OK] $name" | Add-Content $LOG_FILE
        [void]$clean.Add($name)
        Remove-Item $repoPath -Recurse -Force
        continue
    }

    [void]$contaminated.Add($name)

    $replaceFile = "$WORK_DIR\_secrets_replace.txt"
    $SECRETS | Set-Content $replaceFile -Encoding UTF8

    Write-Host "    [*] Running git filter-repo..." -ForegroundColor Cyan
    $filterOut = git -C $repoPath filter-repo --replace-text $replaceFile --force 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "    [ERROR] filter-repo failed: $filterOut" -ForegroundColor Red
        "[ERROR-FILTER] $name | $filterOut" | Add-Content $LOG_FILE
        [void]$errors.Add($name)
        continue
    }
    Write-Host "    [*] History rewritten." -ForegroundColor Cyan

    git -C $repoPath remote add origin "$url.git" 2>&1 | Out-Null
    Write-Host "    [*] Force-pushing..." -ForegroundColor Cyan
    $pushOut = git -C $repoPath push origin $branch --force 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "    [DONE] Force-push OK!" -ForegroundColor Green
        "[CLEANED] $name - force-push OK" | Add-Content $LOG_FILE
    } else {
        Write-Host "    [ERROR] Push failed: $pushOut" -ForegroundColor Red
        "[ERROR-PUSH] $name | $pushOut" | Add-Content $LOG_FILE
        [void]$errors.Add($name)
    }
}

$endTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
"" | Add-Content $LOG_FILE
"=== Scan finished: $endTime ===" | Tee-Object -FilePath $LOG_FILE -Append
"Clean    : $($clean.Count)" | Tee-Object -FilePath $LOG_FILE -Append
"Cleaned  : $($contaminated.Count)" | Tee-Object -FilePath $LOG_FILE -Append
"Errors   : $($errors.Count)" | Tee-Object -FilePath $LOG_FILE -Append

if ($errors.Count -gt 0) {
    "`nErrors in:" | Add-Content $LOG_FILE
    $errors | ForEach-Object { "  - $_" | Add-Content $LOG_FILE }
}

Write-Host "`n=== REPORT ===" -ForegroundColor Magenta
Write-Host "Clean    : $($clean.Count)" -ForegroundColor Green
Write-Host "Cleaned  : $($contaminated.Count)" -ForegroundColor Red
Write-Host "Errors   : $($errors.Count)" -ForegroundColor Yellow
Write-Host "Report   : $LOG_FILE" -ForegroundColor Cyan
