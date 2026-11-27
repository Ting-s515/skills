<#
.SYNOPSIS
  把實作工作派給 GitHub Copilot CLI（非互動 -p + --yolo），只回傳一行 JSON 狀態，
  完整輸出寫入 log 檔，避免 Claude Code 讀進大量 token。

.EXAMPLE
  pwsh -File invoke-copilot.ps1 -PromptFile .scratch/copilot/task.md
#>
param(
    [Parameter(Mandatory)] [string] $PromptFile,
    [string] $Model = 'claude-opus-5.5',
    [string] $ReasoningEffort = 'medium',
    [string] $WorkDir = (Get-Location).Path,
    [string] $LogDir = '',
    [int] $MaxAiCredits = 0,
    # Claude Code 寫好的測試檔；派工前後比對 hash，偵測 Copilot 經 shell 繞過 deny 規則改測試
    [string[]] $TestFiles = @(),
    # 測試檔一律禁止 Copilot 改寫，避免它「改測試讓測試通過」
    # 涵蓋 JS／TS、Java、Python、Go、C# 的常見測試命名；專案慣例不同時以參數覆寫
    [string[]] $ProtectedPaths = @(
        '**/__tests__/**', '**/src/test/**', '**/specs/**', '**/tests/**',
        '**/*.test.ts', '**/*.test.tsx', '**/*.test.js', '**/*.test.jsx',
        '**/*.spec.ts', '**/*.spec.tsx', '**/*.spec.js', '**/*.spec.jsx',
        '**/*Test.java', '**/*Tests.java', '**/test_*.py', '**/*_test.py', '**/*_test.go',
        '**/*Tests.cs', '**/*Test.cs'
    )
)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# `pwsh -File` 會把 -TestFiles "a","b" 綁成單一字串 "a,b"，hash 比對找不到檔案而靜默失效，
# 所以這裡把含逗號的字串拆回陣列；從 PowerShell 呼叫時各項前後還會殘留引號，一併去除。
# ProtectedPaths 的 {a,b} 大括號 glob 內的逗號不可拆
$TestFiles = @($TestFiles | ForEach-Object { $_ -split ',' } | ForEach-Object { $_.Trim().Trim('"', "'") } | Where-Object { $_ })
$ProtectedPaths = @($ProtectedPaths | ForEach-Object { $_ -split ',(?![^{]*\})' } | ForEach-Object { $_.Trim().Trim('"', "'") } | Where-Object { $_ })

if (-not (Test-Path -LiteralPath $PromptFile)) {
    throw "找不到 prompt 檔：$PromptFile"
}
if (-not $LogDir) {
    $LogDir = Join-Path (Split-Path -Parent (Resolve-Path -LiteralPath $PromptFile)) 'logs'
}
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$logFile = Join-Path $LogDir "copilot-$stamp.log"
$usageFile = Join-Path $LogDir "copilot-$stamp.usage.json"
$prompt = Get-Content -LiteralPath $PromptFile -Raw -Encoding utf8

$copilotArgs = @(
    '-C', $WorkDir,
    '-p', $prompt,
    '--model', $Model,
    '--yolo',
    '--no-ask-user',
    '-s',
    '--usage-output-file', $usageFile,
    # deny 規則優先於 --yolo：版控操作與丟棄變更的指令保留給 Claude Code / 使用者
    '--deny-tool', 'shell(git commit)',
    '--deny-tool', 'shell(git push)',
    '--deny-tool', 'shell(git reset)',
    '--deny-tool', 'shell(git checkout)',
    '--deny-tool', 'shell(git restore)',
    '--deny-tool', 'shell(git stash)',
    '--deny-tool', 'shell(git clean)'
)
foreach ($p in $ProtectedPaths) {
    $copilotArgs += @('--deny-tool', "write($p)")
}
if ($ReasoningEffort) {
    $copilotArgs += @('--reasoning-effort', $ReasoningEffort)
}
if ($MaxAiCredits -gt 0) {
    $copilotArgs += @('--max-ai-credits', "$MaxAiCredits")
}

function Get-TestFileHash([string[]] $files) {
    $map = @{}
    foreach ($f in $files) {
        $full = Join-Path $WorkDir $f
        $hash = ''
        if (Test-Path -LiteralPath $full) {
            $hash = (Get-FileHash -LiteralPath $full -Algorithm SHA256).Hash
        }
        $map[$f] = $hash
    }
    return $map
}
$before = Get-TestFileHash $TestFiles

& copilot @copilotArgs *> $logFile
$exitCode = $LASTEXITCODE
$log = Get-Content -LiteralPath $logFile -Raw -Encoding utf8
if ($null -eq $log) { $log = '' }

# 額度與速率限制的訊息字樣取自 `copilot help limits` / `copilot help billing`
$status = 'ok'
if ($log -match "rate limit|You've hit|You've reached your weekly") {
    $status = 'rate_limit'
}
elseif ($log -match 'quota|100% used|Session limit reached|AI credit limit') {
    $status = 'quota'
}
elseif ($exitCode -ne 0) {
    $status = 'failed'
}

$after = Get-TestFileHash $TestFiles
$modifiedTests = @($TestFiles | Where-Object { $before[$_] -ne $after[$_] })
if ($modifiedTests.Count -gt 0 -and $status -eq 'ok') {
    $status = 'tests_modified'
}

$tail = ($log -split "`r?`n" | Where-Object { $_ -and $_ -notmatch '^Warning: Skipped workspace MCP' } | Select-Object -Last 15) -join "`n"

[ordered]@{
    status   = $status
    exitCode = $exitCode
    modifiedTests = $modifiedTests
    log      = $logFile
    usage    = $usageFile
    tail     = $tail
} | ConvertTo-Json -Compress
