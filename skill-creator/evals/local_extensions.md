# 本地擴充 — skill-creator/SKILL.md

此檔案存放於 `evals/`，在 `update-skill-creator` 更新時受保護不被覆蓋。
更新腳本執行後，會自動將「插入內容」區塊插入 SKILL.md 的指定錨點之後。

## 運作流程

1. 先確認 Python 可用：`python --version`（Windows 若不可用，改用 `py --version`）
2. 執行 `python .\update-skill-creator.py`（Windows 可改用 `py .\update-skill-creator.py`；或執行 `.\update-skill-creator.ps1`）→ 官方最新 SKILL.md 覆蓋進來
3. `evals/local_extensions.md` 因 `evals/` 保護機制而存活
4. 腳本偵測錨點 `references/schemas.md` for the full schema，將「插入內容」插入其後
5. 結果：官方更新 + 本地擴充同時保留

## 新增擴充方式

在「插入內容」分隔線之後加入 Markdown 內容，下次執行更新腳本時會自動套用。

## 腳本類型說明（此區塊不會被插入 SKILL.md，僅供 AI 參考）

`skill-creator/scripts/` 下有多支 `.py` 腳本，類型各不相同，請勿混淆：

| 腳本 | 類型 | 說明 |
|---|---|---|
| `scripts/run_eval.py` | **Trigger Evaluation 工具** | 測試 skill description 是否讓 Claude 正確觸發，屬 skill-creator 內部基礎設施。**不適用 `eval-test/MAINTENANCE.md` eval runner 規範，不得套用或升級為 `run_evals.py` 格式。** |
| `scripts/run_loop.py` | skill-creator 內部工具 | 執行 improve 循環，非 eval runner |
| `scripts/quick_validate.py` | skill-creator 內部工具 | 快速驗證 skill 觸發率，非 eval runner |
| `scripts/aggregate_benchmark.py` | skill-creator 內部工具 | 彙整 benchmark 結果，非 eval runner |

> **注意**：`scripts/` 目錄在 `update-skill-creator.py` 執行時會被 GitHub 最新版覆蓋，  
> 任何直接寫在這些檔案頂部的標記都不會持久。類型說明須維護於此檔案（受 `evals/` 保護）。

---

## 插入內容

When creating eval tests, also create `evals/run_evals.py` alongside `evals.json` so external tools (e.g. Codex CLI) can invoke the evals cross-platform. Use Python's built-in `json` module for JSON parsing; do not require `jq`.

建立腳本前，先在腳本上方加入以下規則說明：

````markdown
為什麼使用 Python：Python 可在 Windows/macOS/Linux 以相同程式碼讀取 JSON、處理路徑並呼叫 CLI；避免依賴 Bash、`jq`、Git Bash 或平台特定 shell 語法。

本地規則：Codex eval runner 必須固定使用 `--dangerously-bypass-approvals-and-sandbox`，不要改成 sandbox / approval 模式。這個 runner 預期只在一次性工作區或外部隔離環境中執行。
````

Fill in the actual skill name in the header comment:

```python
#!/usr/bin/env python3
"""Run <skill-name> behavior evals using codex or claude CLI.

Each eval runs twice: with_skill (SKILL.md injected) and without_skill (baseline).
Usage: python evals/run_evals.py [eval-id]   # omit id to run all
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
EVALS_JSON = SCRIPT_DIR / "evals.json"
SKILL_MD = SCRIPT_DIR.parent / "SKILL.md"
OUTPUT_DIR = SCRIPT_DIR.parent / "eval-results"


def fail(message: str) -> None:
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_evals() -> dict:
    if not EVALS_JSON.is_file():
        fail(f"evals.json not found at {EVALS_JSON}")

    with EVALS_JSON.open("r", encoding="utf-8") as file:
        return json.load(file)


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


def run_ai(command_prefix: list[str], prompt: str, output_file: Path) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", encoding="utf-8") as file:
        process = subprocess.Popen(
            [*command_prefix, prompt],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        if process.stdout is not None:
            for line in process.stdout:
                print(line, end="")
                file.write(line)

        return_code = process.wait()
        if return_code != 0:
            fail(f"AI CLI exited with code {return_code}")


def run_with_skill(command_prefix: list[str], skill_instructions: str, prompt: str, output_file: Path) -> None:
    full_prompt = f"""{skill_instructions}

---

Apply the above skill instructions to this task:

{prompt}"""
    run_ai(command_prefix, full_prompt, output_file)


def run_without_skill(command_prefix: list[str], prompt: str, output_file: Path) -> None:
    run_ai(command_prefix, prompt, output_file)


def main() -> int:
    data = load_evals()
    skill_instructions = read_skill_instructions()
    _tool_name, command_prefix = detect_ai_tool()

    skill_name = data.get("skill_name", "<skill-name>")
    evals = data.get("evals", [])
    target_id = sys.argv[1] if len(sys.argv) > 1 else None

    print(f"=== {skill_name} evals ({len(evals)} total) ===")

    for index, eval_case in enumerate(evals):
        eval_id = str(eval_case.get("id", index))
        name = eval_case.get("name") or f"eval-{eval_id}"
        prompt = eval_case.get("prompt")

        if target_id and eval_id != target_id:
            continue

        if not prompt:
            fail(f"eval {eval_id} is missing prompt")

        eval_dir = OUTPUT_DIR / f"eval-{eval_id}"

        print()
        print(f"=== [{eval_id}] {name} ===")
        print(f"Prompt: {prompt}")

        print()
        print("--- with_skill ---")
        run_with_skill(command_prefix, skill_instructions, prompt, eval_dir / "with_skill" / "output.txt")
        print("--- end with_skill ---")

        print()
        print("--- without_skill (baseline) ---")
        run_without_skill(command_prefix, prompt, eval_dir / "without_skill" / "output.txt")
        print("--- end without_skill ---")

        print()
        print(f"[results saved] {eval_dir}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```
