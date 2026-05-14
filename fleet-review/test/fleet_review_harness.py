# [類型] 行為驗證測試共用 Harness
# [說明] 提供 Tracker、assert_contains、assert_not_contains、run_fleet_review 等工具，
#        供 run-test.py（test/）與 run-eval.py（evals/）使用。
#        屬於功能正確性驗證的基礎設施，不是 eval benchmark runner。
# [注意] 不適用 MAINTENANCE.md 的 eval runner 規範，請勿套用。
from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from pathlib import Path


GREEN = "\033[0;32m"
RED = "\033[0;31m"
NC = "\033[0m"


class Tracker:
    def __init__(self) -> None:
        self.pass_count = 0
        self.fail_count = 0
        self.total_count = 0

    def pass_(self, description: str) -> None:
        print(f"  {GREEN}[PASS]{NC} {description}")
        self.pass_count += 1
        self.total_count += 1

    def fail(self, description: str) -> None:
        print(f"  {RED}[FAIL]{NC} {description}")
        self.fail_count += 1
        self.total_count += 1


def assert_contains(tracker: Tracker, description: str, pattern: str, output: str) -> None:
    if pattern in output:
        tracker.pass_(description)
    else:
        tracker.fail(f"{description}  (找不到: '{pattern}')")


def assert_not_contains(tracker: Tracker, description: str, pattern: str, output: str) -> None:
    if pattern not in output:
        tracker.pass_(description)
    else:
        tracker.fail(f"{description}  (不應出現: '{pattern}')")


def assert_contains_any(tracker: Tracker, description: str, first: str, second: str, output: str) -> None:
    if first in output or second in output:
        tracker.pass_(description)
    else:
        tracker.fail(f"{description}  (找不到: '{first}' 或 '{second}')")


def assert_exit_zero(tracker: Tracker, description: str, exit_code: int) -> None:
    if exit_code == 0:
        tracker.pass_(description)
    else:
        tracker.fail(f"{description}  (exit code: {exit_code})")


def count_findings(path: Path) -> int:
    if not path.is_file():
        return 0
    return sum(1 for line in path.read_text(encoding="utf-8", errors="replace").splitlines() if line.startswith("FINDING:"))


def changed_file_count(patch_file: Path) -> int:
    return sum(
        1
        for line in patch_file.read_text(encoding="utf-8", errors="replace").splitlines()
        if line.startswith("diff --git ")
    )


def changed_file_names(patch_file: Path) -> str:
    names: list[str] = []
    for line in patch_file.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.startswith("diff --git "):
            continue
        parts = line.split()
        if len(parts) >= 4:
            names.append(Path(parts[3].removeprefix("b/")).name)
    return ", ".join(names)


def detect_source(output: str, keyword: str) -> bool:
    return re.search(keyword, output, re.IGNORECASE) is not None


def append_issue_report(
    title: str,
    severity: str,
    file_line: str,
    problem: str,
    impact: str,
    finder: str,
    output_file: Path,
) -> None:
    if severity in {"P0", "P1"}:
        section = "### 必須修正（P0 / P1)"
    elif severity == "P2":
        section = "### 建議改善（P2)"
    elif severity == "P3":
        section = "### 輕微問題（P3)"
    else:
        section = "### 建議改善（P2)"

    output_file.write_text(
        output_file.read_text(encoding="utf-8", errors="replace")
        + f"""

{section}

#### {title} — {file_line}
- 問題：{problem}
- 影響：{impact}
- 發現者：{finder}
""",
        encoding="utf-8",
    )


def extract_claude_model(output: str) -> str:
    for line in output.splitlines():
        if line.startswith("AGENT_MODEL: "):
            return line.split(": ", 1)[1]
    return "unknown"


def build_final_report(
    patch_file: Path,
    output_file: Path,
    claude_file: Path,
    codex_file: Path,
    codex_requested_model: str,
) -> None:
    claude_output = claude_file.read_text(encoding="utf-8", errors="replace")
    codex_output = codex_file.read_text(encoding="utf-8", errors="replace") if codex_file.is_file() else ""
    combined = f"{claude_output}\n{codex_output}"
    claude_count = count_findings(claude_file)
    codex_count = count_findings(codex_file)
    raw_count = claude_count + codex_count
    changed_count = changed_file_count(patch_file)
    changed_names = changed_file_names(patch_file)
    claude_model = extract_claude_model(claude_output)

    with tempfile.NamedTemporaryFile("w+", encoding="utf-8", delete=False) as report:
        report_file = Path(report.name)

    with output_file.open("a", encoding="utf-8") as output:
        output.write(
            f"""
艦隊審查 — 原始發現
════════════════════════════════════════════════════════════
基礎分支：main | Diff 來源：fixture patch: {patch_file.name} | 已變更檔案：{changed_count} 個（{changed_names}）
Claude（全面審查）：{claude_count} 個發現
Codex（全面審查）：{codex_count} 個發現
Codex requested model：{codex_requested_model}
代理原始回報：{raw_count} 個（未去重）
"""
        )

    if raw_count == 0 and "NO_FINDINGS" in combined:
        with output_file.open("a", encoding="utf-8") as output:
            output.write(
                f"""去重後問題：0 個
════════════════════════════════════════════════════════════

艦隊審查 — 最終報告
════════════════════════════════════════════════════════════
基礎分支：main | Diff 來源：fixture patch: {patch_file.name} | 已變更檔案：{changed_count} 個
代理：Claude（{claude_model}）+ Codex（requested: {codex_requested_model}）
去重後問題：0 個 → 雙代理確認：0 個，單代理發現：0 個

審查通過：兩個代理均未回報問題。

統計：
  代理原始回報：0 個（未去重）
  去重後問題：0 個
  雙代理確認：0 個，單代理發現：0 個
════════════════════════════════════════════════════════════
"""
            )
        report_file.unlink(missing_ok=True)
        return

    dedup_count = 0
    double_count = 0
    single_count = 0

    if detect_source(combined, r"add|加法|a \+ b|a - b"):
        claude_has = detect_source(claude_output, r"add|加法|a \+ b|a - b")
        codex_has = detect_source(codex_output, r"add|加法|a \+ b|a - b")
        finder = "雙代理確認" if claude_has and codex_has else "⚠️ 單代理發現"
        if claude_has and codex_has:
            double_count += 1
        else:
            single_count += 1
        dedup_count += 1
        append_issue_report(
            "add() 實作錯誤",
            "P1",
            "calculator.js:2",
            "規格要求 add(a, b) 回傳 a + b，但實作回傳 a - b。",
            "所有加法結果錯誤，核心功能不符合規格。",
            finder,
            report_file,
        )

    if detect_source(combined, r"divide|Division by zero|除以零|zero"):
        claude_has = detect_source(claude_output, r"divide|Division by zero|除以零|zero")
        codex_has = detect_source(codex_output, r"divide|Division by zero|除以零|zero")
        finder = "雙代理確認" if claude_has and codex_has else "⚠️ 單代理發現"
        if claude_has and codex_has:
            double_count += 1
        else:
            single_count += 1
        dedup_count += 1
        append_issue_report(
            "divide() 缺少除以零錯誤處理",
            "P1",
            "calculator.js:14",
            "規格要求 divide(x, 0) 必須拋出 Error('Division by zero')，但實作直接除法。",
            "b 為 0 時 JavaScript 會回傳 Infinity，邊界條件不符合規格。",
            finder,
            report_file,
        )

    with output_file.open("a", encoding="utf-8") as output:
        output.write(
            f"""去重後問題：{dedup_count} 個
════════════════════════════════════════════════════════════

艦隊審查 — 最終報告
════════════════════════════════════════════════════════════
基礎分支：main | Diff 來源：fixture patch: {patch_file.name} | 已變更檔案：{changed_count} 個
代理：Claude（{claude_model}）+ Codex（requested: {codex_requested_model}）
去重後問題：{dedup_count} 個 → 雙代理確認：{double_count} 個，單代理發現：{single_count} 個
{report_file.read_text(encoding="utf-8", errors="replace")}

---

### 使用者自行決定（註解類 P3）

本測試未將註解類 P3 納入核心統計；若正式報告納入，必須計入去重後問題與單代理/雙代理統計。

---

統計：
  代理原始回報：{raw_count} 個（未去重）
  去重後問題：{dedup_count} 個
  雙代理確認：{double_count} 個，單代理發現：{single_count} 個
════════════════════════════════════════════════════════════
"""
        )
    report_file.unlink(missing_ok=True)


def run_claude(prompt: str, output_file: Path) -> int:
    claude = shutil.which("claude")
    if not claude:
        output_file.write_text("CLAUDE_FAILED: exit_code=127\nclaude CLI not found\n", encoding="utf-8")
        return 127

    command = [
        claude,
        "-p",
        "--model",
        "claude-sonnet-4-6",
        "--effort",
        "high",
        "--permission-mode",
        "dontAsk",
        "--tools",
        "Read",
        "--no-session-persistence",
        prompt,
    ]
    with output_file.open("w", encoding="utf-8") as output:
        result = subprocess.run(command, stdout=output, stderr=subprocess.STDOUT, text=True, check=False)

    if result.returncode == 0:
        return 0

    original = output_file.read_text(encoding="utf-8", errors="replace")
    output_file.write_text(f"CLAUDE_FAILED: exit_code={result.returncode}\n{original}", encoding="utf-8")
    return result.returncode


def run_codex(prompt: str, output_file: Path, trace_file: Path, requested_model: str) -> int:
    codex = shutil.which("codex")
    if not codex:
        trace_file.write_text("codex CLI not found\n", encoding="utf-8")
        return 127

    command = [
        codex,
        "exec",
        "-",
        "-m",
        requested_model,
        "-c",
        'model_reasoning_effort="high"',
        "-s",
        "read-only",
        "--ephemeral",
        "-o",
        str(output_file),
    ]
    with trace_file.open("w", encoding="utf-8") as trace:
        result = subprocess.run(
            command,
            input=prompt,
            stdout=trace,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    return result.returncode


def run_fleet_review(patch_file: Path, spec_file: Path, output_file: Path) -> int:
    patch_file = patch_file.resolve()
    spec_file = spec_file.resolve()
    output_file.parent.mkdir(parents=True, exist_ok=True)

    spec_content = spec_file.read_text(encoding="utf-8", errors="replace")
    claude_prompt = f"""你是程式碼審查代理。請審查以下 diff 的變更，並閱讀相關原始檔以了解完整上下文。

Diff 檔案：{patch_file}

規格文檔：
{spec_content}

審查方向：
1. 規格符合度：規格中要求的功能是否完整實作？定義的 API / 資料結構是否一致？邊界條件與錯誤處理是否涵蓋？是否有規格以外的多餘實作？
2. 邏輯正確性：差一錯誤、條件反轉、錯誤比較、破壞不變條件
3. 安全性：注入攻擊、授權繞過、敏感資料洩露、缺少輸入驗證
4. 邊界情況與錯誤處理：資源洩漏、未處理例外、邊界條件
5. 效能：N+1 查詢、無界迴圈、記憶體分配問題
6. 型別安全：不安全斷言、型別縮窄缺口、序列化邊界

絕不修改任何程式碼（唯讀）。

每個發現輸出以下精確格式：
FINDING:
  severity: P0|P1|P2|P3
  file: <路徑>
  line: <行號或範圍>
  title: <一行摘要>
  detail: <2-3 句話說明問題及其影響>

嚴重程度：P0=生產崩潰/安全漏洞 P1=功能錯誤 P2=條件性問題 P3=輕微問題
若無發現，輸出：NO_FINDINGS

最後一行必須輸出：AGENT_MODEL: <你實際使用的模型 ID，例如 claude-sonnet-4-6>
"""

    codex_prompt = f"""你是程式碼審查代理。請用你的 Read 工具依序讀取下列兩個檔案，再審查並輸出發現。

規格文檔路徑（請讀取）：{spec_file}
Diff 檔案路徑（請讀取）：{patch_file}

審查方向：
1. 規格符合度：規格中要求的功能是否完整實作？
2. 邏輯正確性：差一錯誤、條件反轉、錯誤比較
3. 安全性：注入攻擊、授權繞過、敏感資料洩露
4. 邊界情況與錯誤處理：資源洩漏、未處理例外
5. 效能：N+1 查詢、無界迴圈
6. 型別安全：不安全斷言、型別縮窄缺口

絕不修改任何程式碼（唯讀）。

每個發現輸出以下精確格式：
FINDING:
  severity: P0|P1|P2|P3
  file: <路徑>
  line: <行號或範圍>
  title: <一行摘要>
  detail: <2-3 句話說明問題及其影響>

嚴重程度：P0=生產崩潰/安全漏洞 P1=功能錯誤 P2=條件性問題 P3=輕微問題
若無發現，輸出：NO_FINDINGS
"""

    temp_path = Path(tempfile.mkdtemp())
    try:
        claude_output_file = temp_path / "fleet-review-claude.txt"
        codex_output_file = temp_path / "codex-output.txt"
        codex_trace_file = temp_path / "codex-trace.txt"

        claude_exit = run_claude(claude_prompt, claude_output_file)
        codex_requested_model = "gpt-5.5"
        codex_exit = run_codex(codex_prompt, codex_output_file, codex_trace_file, codex_requested_model)

        with output_file.open("w", encoding="utf-8") as output:
            output.write("=== CLAUDE OUTPUT ===\n")
            output.write(claude_output_file.read_text(encoding="utf-8", errors="replace"))
            output.write("\n=== CODEX OUTPUT ===\n")
            if codex_exit == 0 and codex_output_file.is_file() and codex_output_file.stat().st_size > 0:
                output.write(codex_output_file.read_text(encoding="utf-8", errors="replace"))
            else:
                output.write(f"CODEX_FAILED: exit_code={codex_exit}\n")
            output.write(f"\nCODEX_REQUESTED_MODEL: {codex_requested_model}\n")

        build_final_report(patch_file, output_file, claude_output_file, codex_output_file, codex_requested_model)
        return claude_exit
    finally:
        shutil.rmtree(temp_path, ignore_errors=True)
