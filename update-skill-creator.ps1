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
    if (-not (Select-String -Path $skillMd -Pattern 'evals/run_evals_bdd\.py' -Quiet)) {
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

# === 套用本地 patches（移除 without_skill / baseline，對齊 BDD eval 流程）===
if (-not $skillMd) { $skillMd = Join-Path $TARGET_DIR "SKILL.md" }
if (-not $utf8NoBom) { $utf8NoBom = [System.Text.UTF8Encoding]::new($false) }
if (Test-Path $skillMd) {
    Write-Host ">>> 套用本地 patches..."

    function Patch-SkillMd {
        param([string]$Content, [string]$Old, [string]$New, [string]$Name)
        $oldNorm = $Old -replace '\r\n', "`n"
        if (-not $Content.Contains($oldNorm)) {
            throw "Patch [$Name] 失敗：找不到目標字串，官方 SKILL.md 可能已更動，請確認此 patch 是否仍適用。"
        }
        return $Content.Replace($oldNorm, ($New -replace '\r\n', "`n"))
    }

    $patchContent = ([System.IO.File]::ReadAllText($skillMd)) -replace '\r\n', "`n"

    # ── Patch 1：evals.json 範例移除 expected_output / files，補 name + expectations ──
    $patchContent = Patch-SkillMd $patchContent @'
    {
      "id": 1,
      "prompt": "User's task prompt",
      "expected_output": "Description of expected result",
      "files": []
    }
'@ @'
    {
      "id": 1,
      "name": "descriptive-eval-name",
      "prompt": "User's task prompt",
      "expectations": []
    }
'@ "evals.json 範例欄位"

    # ── Patch 2：schema 備註 assertions → expectations ──
    $patchContent = Patch-SkillMd $patchContent @'
See `references/schemas.md` for the full schema (including the `assertions` field, which you'll add later).
'@ @'
See `references/schemas.md` for the full schema (including the `expectations` field, which you'll fill in later).
'@ "schema 備註術語"

    # ── Patch 3：Step 1 標題 + 說明，移除 Baseline run 區塊 ──
    $patchContent = Patch-SkillMd $patchContent @'
### Step 1: Spawn all runs (with-skill AND baseline) in the same turn

For each test case, spawn two subagents in the same turn — one with the skill, one without. This is important: don't spawn the with-skill runs first and then come back for baselines later. Launch everything at once so it all finishes around the same time.

**With-skill run:**

```
Execute this task:
- Skill path: <path-to-skill>
- Task: <eval prompt>
- Input files: <eval files if any, or "none">
- Save outputs to: <workspace>/iteration-<N>/eval-<ID>/with_skill/outputs/
- Outputs to save: <what the user cares about — e.g., "the .docx file", "the final CSV">
```

**Baseline run** (same prompt, but the baseline depends on context):
- **Creating a new skill**: no skill at all. Same prompt, no skill path, save to `without_skill/outputs/`.
- **Improving an existing skill**: the old version. Before editing, snapshot the skill (`cp -r <skill-path> <workspace>/skill-snapshot/`), then point the baseline subagent at the snapshot. Save to `old_skill/outputs/`.
'@ @'
### Step 1: Spawn all with-skill runs in the same turn

For each test case, spawn one subagent with the skill. Launch all of them at once so they finish around the same time.

**With-skill run:**

```
Execute this task:
- Skill path: <path-to-skill>
- Task: <eval prompt>
- Input files: <eval files if any, or "none">
- Save outputs to: <workspace>/iteration-<N>/eval-<ID>/with_skill/outputs/
- Outputs to save: <what the user cares about — e.g., "the .docx file", "the final CSV">
```
'@ "Step 1 with-skill only"

    # ── Patch 4：Step 2 assertions → expectations，加 run_evals_bdd.py 執行指令 ──
    $patchContent = Patch-SkillMd $patchContent @'
### Step 2: While runs are in progress, draft assertions

Don't just wait for the runs to finish — you can use this time productively. Draft quantitative assertions for each test case and explain them to the user. If assertions already exist in `evals/evals.json`, review them and explain what they check.

Good assertions are objectively verifiable and have descriptive names — they should read clearly in the benchmark viewer so someone glancing at the results immediately understands what each one checks. Subjective skills (writing style, design quality) are better evaluated qualitatively — don't force assertions onto things that need human judgment.

Update the `eval_metadata.json` files and `evals/evals.json` with the assertions once drafted. Also explain to the user what they'll see in the viewer — both the qualitative outputs and the quantitative benchmark.
'@ @'
### Step 2: While runs are in progress, draft expectations

Don't just wait for the runs to finish — you can use this time productively. Draft quantitative expectations for each test case and explain them to the user. If expectations already exist in `evals/evals.json`, review them and explain what they check.

Good expectations are objectively verifiable and have descriptive names — they should read clearly in the benchmark viewer so someone glancing at the results immediately understands what each one checks. Subjective skills (writing style, design quality) are better evaluated qualitatively — don't force expectations onto things that need human judgment.

Update the workspace `eval_metadata.json` files with `assertions` (used by the grader subagent) and `evals/evals.json` with `expectations` (used by the BDD runner). Also explain to the user what they'll see in the viewer — both the qualitative outputs and the quantitative benchmark.

Once `expectations` are filled in and fixture directories populated, run the BDD runner to get a quantitative pass rate:

```bash
python evals/run_evals_bdd.py
```

This outputs `X/Y expectations passed` — the most direct quality metric per iteration.
'@ "Step 2 expectations + BDD runner"

    # ── Patch 5：Step 4 benchmark 移除 delta / baseline counterpart ──
    $patchContent = Patch-SkillMd $patchContent @'
   This produces `benchmark.json` and `benchmark.md` with pass_rate, time, and tokens for each configuration, with mean ± stddev and the delta. If generating benchmark.json manually, see `references/schemas.md` for the exact schema the viewer expects.
Put each with_skill version before its baseline counterpart.
'@ @'
   This produces `benchmark.json` and `benchmark.md` with pass_rate, time, and tokens for each test run. If generating benchmark.json manually, see `references/schemas.md` for the exact schema the viewer expects.
'@ "benchmark delta"

    # ── Patch 6：迭代迴圈移除 including baseline runs ──
    $patchContent = Patch-SkillMd $patchContent @'
2. Rerun all test cases into a new `iteration-<N+1>/` directory, including baseline runs. If you're creating a new skill, the baseline is always `without_skill` (no skill) — that stays the same across iterations. If you're improving an existing skill, use your judgment on what makes sense as the baseline: the original version the user came in with, or the previous iteration.
'@ @'
2. Rerun all test cases into a new `iteration-<N+1>/` directory with the updated skill.
'@ "迭代迴圈 baseline"

    # ── Patch 7：Claude.ai 移除 Skip baseline runs ──
    $patchContent = Patch-SkillMd $patchContent @'
**Running test cases**: No subagents means no parallel execution. For each test case, read the skill's SKILL.md, then follow its instructions to accomplish the test prompt yourself. Do them one at a time. This is less rigorous than independent subagents (you wrote the skill and you're also running it, so you have full context), but it's a useful sanity check — and the human review step compensates. Skip the baseline runs — just use the skill to complete the task as requested.
'@ @'
**Running test cases**: No subagents means no parallel execution. For each test case, read the skill's SKILL.md, then follow its instructions to accomplish the task yourself. Do them one at a time. This is less rigorous than independent subagents (you wrote the skill and you're also running it, so you have full context), but it's a useful sanity check — and the human review step compensates.
'@ "Claude.ai baseline"

    # ── Patch 8：Claude.ai Benchmarking ──
    $patchContent = Patch-SkillMd $patchContent @'
**Benchmarking**: Skip the quantitative benchmarking — it relies on baseline comparisons which aren't meaningful without subagents. Focus on qualitative feedback from the user.
'@ @'
**Benchmarking**: Skip the quantitative benchmarking — it requires subagents to run `run_evals_bdd.py`. Focus on qualitative feedback from the user.
'@ "Claude.ai benchmarking"

    # ── Patch 9：Cowork 移除 run baselines ──
    $patchContent = Patch-SkillMd $patchContent @'
- You have subagents, so the main workflow (spawn test cases in parallel, run baselines, grade, etc.) all works.
'@ @'
- You have subagents, so the main workflow (spawn test cases in parallel, grade, etc.) all works.
'@ "Cowork baseline"

    [System.IO.File]::WriteAllText($skillMd, $patchContent, $utf8NoBom)

    if (Select-String -Path $skillMd -Pattern 'without_skill/outputs' -Quiet) {
        throw "Patch 驗證失敗：SKILL.md 仍含 'without_skill/outputs'，請檢查 Step 1 patch 是否仍匹配官方 SKILL.md。"
    }
    if (-not (Select-String -Path $skillMd -Pattern 'python evals/run_evals_bdd\.py' -Quiet)) {
        throw "Patch 驗證失敗：SKILL.md 缺少 BDD runner 執行指令，Step 2 patch 可能失敗。"
    }
    Write-Host ">>> 已套用本地 patches (9 項)"
}

Write-Host ">>> 完成！skill-creator 已更新至最新版本。"
