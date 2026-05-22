# 本地擴充 — skill-creator-plus/SKILL.md

此檔案存放於 `evals/`，在 `update-skill-creator` 更新時受保護不被覆蓋。
更新腳本執行後，會自動將「插入內容」區塊插入 SKILL.md 的指定錨點之後。

## 運作流程

1. 先確認 Python 可用：`python --version`（Windows 若不可用，改用 `py --version`）
2. 執行 `python .\update-skill-creator.py`（Windows 可改用 `py .\update-skill-creator.py`）→ 官方最新 SKILL.md 覆蓋進來
3. `evals/local_extensions.md` 因 `evals/` 保護機制而存活
4. 腳本偵測錨點 `references/schemas.md` for the full schema，將「插入內容」插入其後
5. 結果：官方更新 + 本地擴充同時保留

## 新增擴充方式

在「插入內容」分隔線之後加入 Markdown 內容，下次執行更新腳本時會自動套用。

## 腳本類型說明（此區塊不會被插入 SKILL.md，僅供 AI 參考）

`skill-creator-plus/scripts/` 下有多支 `.py` 腳本，類型各不相同，請勿混淆：

| 腳本 | 類型 | 說明 |
|---|---|---|
| `scripts/run_eval.py` | **Trigger Evaluation 工具** | 測試 skill description 是否讓 Claude 正確觸發，屬 skill-creator-plus 內部基礎設施。**不適用 `skill-creator-plus/eval-test/MAINTENANCE.md` eval runner 規範，不得套用或升級為 `run_evals_bdd.py` 格式。** |
| `scripts/run_loop.py` | skill-creator-plus 內部工具 | 執行 improve 循環，非 eval runner |
| `scripts/quick_validate.py` | skill-creator-plus 內部工具 | 快速驗證 skill 觸發率，非 eval runner |
| `scripts/aggregate_benchmark.py` | skill-creator-plus 內部工具 | 彙整 benchmark 結果，非 eval runner |

> **注意**：`scripts/` 目錄在 `update-skill-creator.py` 執行時會被 GitHub 最新版覆蓋，  
> 任何直接寫在這些檔案頂部的標記都不會持久。類型說明須維護於此檔案（受 `evals/` 保護）。

---

## 插入內容

When creating eval tests, also create `evals/run_evals_bdd.py` alongside `evals.json` — do this proactively even if the user only asks for eval tests without mentioning the runner. This is the canonical eval runner — it computes the diff in Python, embeds diff + spec + expectations into a self-contained prompt, and the AI self-grades each expectation with `E1: PASS/FAIL — evidence`. Works cross-platform and cross-tool (Claude CLI and Codex CLI) without requiring filesystem access from the AI.

**Fixture structure** — create `evals/fixtures/eval-<id>/` for each eval:

```
evals/fixtures/eval-1/
├── base/          # file(s) before the change (empty dir = new file scenario)
├── staged/        # file(s) after the change (the code under review)
└── spec/          # optional spec/requirements docs fed to the AI
```

The `expectations` field in `evals.json` is what the BDD runner grades. Fill them in now or after the first few runs once you know what to look for.

為每個 eval 建立 fixture 目錄（`staged/` 為必要，即使內容為空）：

- **有檔案輸入的技能**（code-reviewer、file transformer 等）：將變更前的檔案放入 `base/`，變更後的放入 `staged/`。
- **純文字輸出技能**（writing、summarization 等）：`base/` 與 `staged/` 保持空目錄即可；diff 為空時 BDD runner 仍能根據 prompt 回應進行評分。
- **有規格文檔**：放入 `spec/`，runner 會自動注入 prompt。

建立腳本前，先在腳本上方加入以下規則說明：

````markdown
為什麼使用 Python：Python 可在 Windows/macOS/Linux 以相同程式碼讀取 JSON、處理路徑並呼叫 CLI；避免依賴 Bash、`jq`、Git Bash 或平台特定 shell 語法。

本地規則：Codex eval runner 必須固定使用 `--dangerously-bypass-approvals-and-sandbox`，不要改成 sandbox / approval 模式。這個 runner 預期只在一次性工作區或外部隔離環境中執行。
````

Fill in the actual skill name in the header comment:

```python
#!/usr/bin/env python3
"""BDD-style self-grading eval runner for <skill-name> skill.

【用途】
  讀取 evals/fixtures/eval-<id>/ 下的 base、staged、spec 目錄，
  以 Python difflib 計算 base→staged 的 unified diff，連同 spec 文檔、
  evals.json 的 expectations 清單，一起 embed 進單一 prompt 傳給 AI。
  AI 完成任務後在同一輸出內自評分，格式為：
    E1: PASS — 從輸出摘錄的證據（一句話）
    E2: FAIL — 說明為何未達到
  runner 解析 Grading 區塊，統計通過率並輸出 X/Y expectations passed。

【fixture 結構】
  evals/fixtures/eval-<id>/
  ├── base/    # 變更前的檔案（空目錄 = 新增檔案情境）
  ├── staged/  # 變更後的檔案（被審查的程式碼）—— 必要
  └── spec/    # 規格文檔（選填，有則自動注入 prompt）

【為什麼用 Python】
  Python 可在 Windows/macOS/Linux 以相同程式碼讀取 JSON、處理路徑並呼叫 CLI；
  避免依賴 Bash、jq、Git Bash 或平台特定 shell 語法。

本地規則：Codex eval runner 必須固定使用 `--dangerously-bypass-approvals-and-sandbox`，
不要改成 sandbox / approval 模式。這個 runner 預期只在一次性工作區或外部隔離環境中執行。

所有 eval 全部並行啟動（max_workers=eval 數量），總執行時間 ≈ 最慢的單一 eval，而非全部加總。

Usage:
    python evals/run_evals_bdd.py           # 執行全部 eval
    python evals/run_evals_bdd.py 1         # 只執行 eval id=1
"""
from __future__ import annotations

import difflib
import json
import re
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
EVALS_JSON = SCRIPT_DIR / "evals.json"
SKILL_MD = SCRIPT_DIR.parent / "SKILL.md"
FIXTURES_DIR = SCRIPT_DIR / "fixtures"
OUTPUT_DIR = SCRIPT_DIR.parent / "eval-results-bdd"

DEFAULT_TIMEOUT = 300


_GRADING_SUFFIX_TEMPLATE = """\

---

## 評分任務

請在完成上方的任務後，接著評分以下每一條 Expectation。
每條獨立一行，格式固定為：

En: PASS — 從你的輸出摘錄的證據（一句話）
En: FAIL — 說明為何未達到

（n 為 Expectation 編號，例如 E1: PASS — ...）

### Expectations 清單

__EXPECTATIONS_BLOCK__

---

## 輸出規範

1. 先完整輸出任務結果（格式遵照 skill 指示）
2. 輸出一行分隔線：`---`
3. 輸出標題 `## Grading`
4. 逐行輸出評分結果（E1、E2 … 順序對應上方清單）
"""


@dataclass
class GradingResult:
    eval_id: str
    eval_name: str
    expectations: list[str]
    grades: list[tuple[str, str]]   # (PASS|FAIL, evidence)
    raw_output: str
    duration_seconds: float
    timed_out: bool
    exit_code: int
    error: str = ""

    @property
    def pass_count(self) -> int:
        return sum(1 for status, _ in self.grades if status.upper() == "PASS")

    @property
    def total(self) -> int:
        return len(self.expectations)


def fail(message: str) -> None:
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_evals() -> dict:
    if not EVALS_JSON.is_file():
        fail(f"evals.json not found at {EVALS_JSON}")
    with EVALS_JSON.open("r", encoding="utf-8") as f:
        return json.load(f)


def read_skill_instructions() -> str:
    if not SKILL_MD.is_file():
        fail(f"SKILL.md not found at {SKILL_MD}")
    return SKILL_MD.read_text(encoding="utf-8")


def detect_ai_tool() -> tuple[str, list[str]]:
    codex = shutil.which("codex")
    if codex:
        print("[tool] codex")
        return "codex", [codex, "exec", "--dangerously-bypass-approvals-and-sandbox"]
    claude = shutil.which("claude")
    if claude:
        print("[tool] claude")
        return "claude", [claude, "-p"]
    fail("neither codex nor claude CLI found")


def compute_unified_diff(base_dir: Path, staged_dir: Path) -> str:
    base_files: set[Path] = set()
    staged_files: set[Path] = set()

    if base_dir.exists():
        base_files = {f.relative_to(base_dir) for f in base_dir.rglob("*") if f.is_file()}
    if staged_dir.exists():
        staged_files = {f.relative_to(staged_dir) for f in staged_dir.rglob("*") if f.is_file()}

    all_rel = sorted(base_files | staged_files)
    chunks: list[str] = []

    for rel in all_rel:
        base_path = base_dir / rel
        staged_path = staged_dir / rel

        base_lines = base_path.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True) if base_path.exists() else []
        staged_lines = staged_path.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True) if staged_path.exists() else []

        diff_lines = list(difflib.unified_diff(
            base_lines,
            staged_lines,
            fromfile=f"a/{rel.as_posix()}",
            tofile=f"b/{rel.as_posix()}",
        ))
        if diff_lines:
            chunks.extend(diff_lines)

    return "".join(chunks)


def read_spec_files(spec_dir: Path) -> dict[str, str]:
    if not spec_dir.exists():
        return {}
    return {
        f.name: f.read_text(encoding="utf-8", errors="replace")
        for f in spec_dir.rglob("*") if f.is_file()
    }


def build_prompt(
    skill_instructions: str,
    eval_prompt: str,
    unified_diff: str,
    spec_files: dict[str, str],
    expectations: list[str],
) -> str:
    spec_section = ""
    if spec_files:
        parts = []
        for name, content in spec_files.items():
            parts.append(f"### 規格文檔：{name}\n\n{content}")
        spec_section = "\n\n".join(parts) + "\n\n"

    expectations_block = "\n".join(
        f"E{i + 1}. {exp}" for i, exp in enumerate(expectations)
    )

    grading_suffix = _GRADING_SUFFIX_TEMPLATE.replace("__EXPECTATIONS_BLOCK__", expectations_block)

    return (
        f"{skill_instructions}\n\n"
        f"---\n\n"
        f"Apply the above skill instructions to this task.\n\n"
        f"## 重要說明\n\n"
        f"以下已提供所有所需資訊（diff、規格文檔），不需要執行 shell 指令或讀取檔案；"
        f"但若 skill 指示要求輸出存檔，仍須依該指示建立輸出檔案。\n\n"
        f"{spec_section}"
        f"## Git diff（base → staged）\n\n"
        f"```diff\n{unified_diff}```\n\n"
        f"## 使用者的請求\n\n"
        f"{eval_prompt}"
        f"{grading_suffix}"
    )


def run_ai(command_prefix: list[str], prompt: str, output_file: Path, timeout: int) -> tuple[int, bool]:
    output_file.parent.mkdir(parents=True, exist_ok=True)

    process = subprocess.Popen(
        command_prefix,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    try:
        stdout, _ = process.communicate(input=prompt, timeout=timeout)
        output_file.write_text(stdout, encoding="utf-8")
        return process.returncode, False
    except subprocess.TimeoutExpired as exc:
        process.kill()
        stdout, _ = process.communicate()
        partial = exc.output or stdout or ""
        output_file.write_text(f"{partial}\n[timeout] killed after {timeout}s\n", encoding="utf-8")
        return -1, True


def parse_grading(raw: str, expected_count: int) -> list[tuple[str, str]]:
    pattern = re.compile(r"E(\d+):\s*(PASS|FAIL)\s*[—\-–]\s*(.+)", re.IGNORECASE)
    found: dict[int, tuple[str, str]] = {}

    for line in raw.splitlines():
        m = pattern.search(line)
        if m:
            idx = int(m.group(1))
            status = m.group(2).upper()
            evidence = m.group(3).strip()
            found[idx] = (status, evidence)

    return [
        found.get(i + 1, ("FAIL", "（未找到對應評分行）"))
        for i in range(expected_count)
    ]


def run_bdd_eval(
    eval_id: str,
    eval_name: str,
    prompt: str,
    fixture_dir: Path,
    expectations: list[str],
    skill_instructions: str,
    command_prefix: list[str],
    timeout: int,
) -> GradingResult:
    base_dir = fixture_dir / "base"
    staged_dir = fixture_dir / "staged"
    spec_dir = fixture_dir / "spec"

    unified_diff = compute_unified_diff(base_dir, staged_dir)
    spec_files = read_spec_files(spec_dir)

    full_prompt = build_prompt(
        skill_instructions=skill_instructions,
        eval_prompt=prompt,
        unified_diff=unified_diff,
        spec_files=spec_files,
        expectations=expectations,
    )

    output_file = OUTPUT_DIR / f"eval-{eval_id}" / "output.txt"
    start = time.time()
    exit_code, timed_out = run_ai(command_prefix, full_prompt, output_file, timeout)
    duration = time.time() - start

    raw = output_file.read_text(encoding="utf-8", errors="replace") if output_file.exists() else ""
    grades = parse_grading(raw, len(expectations))

    return GradingResult(
        eval_id=eval_id,
        eval_name=eval_name,
        expectations=expectations,
        grades=grades,
        raw_output=raw,
        duration_seconds=duration,
        timed_out=timed_out,
        exit_code=exit_code,
    )


def main() -> int:
    data = load_evals()
    skill_instructions = read_skill_instructions()
    _tool_name, command_prefix = detect_ai_tool()

    skill_name = data.get("skill_name", "<skill-name>")
    evals = data.get("evals", [])
    target_id = sys.argv[1] if len(sys.argv) > 1 else None

    if target_id:
        evals = [e for e in evals if str(e.get("id", "")) == target_id]

    if not evals:
        print("No eval tasks to run.")
        return 0

    print(f"=== {skill_name} BDD evals ({len(evals)} total) ===")
    print(f"Launching {len(evals)} runs in parallel...\n")

    results: list[GradingResult] = []
    with ThreadPoolExecutor(max_workers=len(evals)) as executor:
        futures = {
            executor.submit(
                run_bdd_eval,
                str(e.get("id", i)),
                e.get("name") or f"eval-{e.get('id', i)}",
                e.get("prompt", ""),
                FIXTURES_DIR / f"eval-{e.get('id', i)}",
                e.get("expectations") or e.get("assertions", []),
                skill_instructions,
                command_prefix,
                DEFAULT_TIMEOUT,
            ): str(e.get("id", i))
            for i, e in enumerate(evals)
        }

        for future in as_completed(futures):
            eval_id = futures[future]
            try:
                result = future.result()
                status = "TIMEOUT" if result.timed_out else ("OK" if result.exit_code == 0 else "FAIL")
                print(f"  [{status}] eval-{result.eval_id} {result.eval_name} ({result.duration_seconds:.1f}s) "
                      f"— {result.pass_count}/{result.total} passed")
                results.append(result)
            except Exception as exc:
                print(f"  [ERROR] eval-{eval_id}: {exc}")

    print()
    print("=== Detailed Results ===")
    total_pass = 0
    total_expectations = 0

    for result in sorted(results, key=lambda r: r.eval_id):
        print(f"\n[eval-{result.eval_id}] {result.eval_name}  ({result.pass_count}/{result.total})")
        for i, (exp, (status, evidence)) in enumerate(zip(result.expectations, result.grades)):
            icon = "PASS" if status == "PASS" else "FAIL"
            print(f"  {icon} E{i+1}: {status}")
            print(f"       Exp: {exp[:80]}")
            print(f"       Evi: {evidence[:80]}")
        total_pass += result.pass_count
        total_expectations += result.total

    print()
    print(f"=== Summary: {total_pass}/{total_expectations} expectations passed ===")
    print(f"Results: {OUTPUT_DIR}")

    return 0 if total_pass == total_expectations else 1


if __name__ == "__main__":
    # On Windows, re-exec with Python UTF-8 mode to avoid cp950 encoding errors.
    # Setting PYTHONUTF8=1 + -X utf8 forces UTF-8 at the interpreter level,
    # which is more reliable than reconfiguring sys.stdout after the fact.
    if sys.platform == "win32" and not sys.flags.utf8_mode:
        import os
        env = os.environ.copy()
        env["PYTHONUTF8"] = "1"
        result = subprocess.run(
            [sys.executable, "-X", "utf8", __file__] + sys.argv[1:],
            env=env,
        )
        sys.exit(result.returncode)
    raise SystemExit(main())
```
