# 從 anthropics/claude-plugins-official 拉取最新 skill-creator 覆蓋本地
# ./update-skill-creator.ps1

$ErrorActionPreference = "Stop"

$REPO_URL  = "https://github.com/anthropics/claude-plugins-official.git"
$SKILL_PATH = "plugins/skill-creator/skills/skill-creator"
$TARGET_DIR = "$env:USERPROFILE\.claude\skills\skill-creator"
$TMP_DIR    = Join-Path ([System.IO.Path]::GetTempPath()) ([System.Guid]::NewGuid())

Write-Host ">>> 拉取最新 skill-creator..."
New-Item -ItemType Directory -Force -Path $TMP_DIR | Out-Null
git clone --depth=1 --filter=blob:none --sparse $REPO_URL $TMP_DIR --quiet
Push-Location $TMP_DIR
git sparse-checkout set $SKILL_PATH

Write-Host ">>> 覆蓋本地 $TARGET_DIR ..."

# 備份 evals（本地自定義，不覆蓋）
$EVALS_BACKUP = Join-Path ([System.IO.Path]::GetTempPath()) ([System.Guid]::NewGuid())
New-Item -ItemType Directory -Force -Path $EVALS_BACKUP | Out-Null
$evalsDir = Join-Path $TARGET_DIR "evals"
if (Test-Path $evalsDir) {
    Copy-Item -Recurse -Force "$evalsDir\*" $EVALS_BACKUP -ErrorAction SilentlyContinue
}

# 清除舊內容
foreach ($item in @("agents","assets","eval-viewer","references","scripts","LICENSE.txt","SKILL.md")) {
    $p = Join-Path $TARGET_DIR $item
    if (Test-Path $p) { Remove-Item -Recurse -Force $p }
}

# 複製官方最新內容
$source = Join-Path $TMP_DIR $SKILL_PATH
Copy-Item -Recurse -Force "$source\*" $TARGET_DIR

# 還原 evals
Remove-Item -Recurse -Force $evalsDir -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path (Join-Path $evalsDir "files") | Out-Null
if ((Get-ChildItem $EVALS_BACKUP -ErrorAction SilentlyContinue).Count -gt 0) {
    Copy-Item -Recurse -Force "$EVALS_BACKUP\*" $evalsDir
}

Pop-Location
Remove-Item -Recurse -Force $TMP_DIR, $EVALS_BACKUP

# 套用本地擴充（evals/local_extensions.md「## 插入內容」之後 → 插入 SKILL.md 錨點之後）
$localExt = Join-Path $evalsDir "local_extensions.md"
if (Test-Path $localExt) {
    $skillMd = Join-Path $TARGET_DIR "SKILL.md"
    $anchor = 'references/schemas.md` for the full schema'
    $extLines = [System.IO.File]::ReadAllLines($localExt)
    $sepMatch = $extLines | Select-String -Pattern '^## 插入內容$' | Select-Object -First 1
    if (-not $sepMatch) {
        throw "找不到 local_extensions.md 的「## 插入內容」區塊，無法套用本地擴充。"
    }

    $insertContent = (($extLines | Select-Object -Skip $sepMatch.LineNumber) -join "`n").Trim("`r", "`n")
    if ([string]::IsNullOrWhiteSpace($insertContent)) {
        throw "local_extensions.md 的「## 插入內容」區塊沒有可插入內容，無法套用本地擴充。"
    }

    $skillContent = [System.IO.File]::ReadAllText($skillMd)
    $idx = $skillContent.IndexOf($anchor)
    if ($idx -lt 0) {
        throw "找不到 SKILL.md 錨點：$anchor，無法套用本地擴充。"
    }

    $endOfLine = $skillContent.IndexOf("`n", $idx)
    if ($endOfLine -lt 0) { $endOfLine = $skillContent.Length }
    $skillContent = $skillContent.Substring(0, $endOfLine + 1) + "`n" + $insertContent + "`n" + $skillContent.Substring($endOfLine + 1)
    $utf8NoBom = [System.Text.UTF8Encoding]::new($false)
    [System.IO.File]::WriteAllText($skillMd, $skillContent, $utf8NoBom)
    if (-not (Select-String -Path $skillMd -Pattern 'evals/run_evals\.py' -Quiet)) {
        throw "本地擴充未成功插入 SKILL.md。"
    }
    if (-not (Select-String -Path $skillMd -Pattern '本地規則：Codex eval runner' -Quiet)) {
        throw "本地擴充缺少 Codex eval runner 本地規則。"
    }
    if (-not (Select-String -Path $skillMd -Pattern '--dangerously-bypass-approvals-and-sandbox' -Quiet)) {
        throw "本地擴充缺少 Codex bypass sandbox 參數。"
    }
    Write-Host ">>> 已套用本地擴充 (local_extensions.md)"
}

Write-Host ">>> 完成！skill-creator 已更新至最新版本。"
