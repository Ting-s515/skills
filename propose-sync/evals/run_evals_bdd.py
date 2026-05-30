#!/usr/bin/env python3
"""Workspace-style BDD eval runner for propose-sync.

Runs each fixture in an isolated workspace, invokes Codex with the propose-sync
skill instructions, then grades the resulting spec.md deterministically.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
EVALS_JSON = SCRIPT_DIR / "evals.json"
SKILL_MD = SKILL_DIR / "SKILL.md"
FIXTURES_DIR = SCRIPT_DIR / "files"
OUTPUT_DIR = SKILL_DIR / "eval-results-bdd"

DEFAULT_TIMEOUT = 300


@dataclass
class AssertionResult:
    name: str
    passed: bool
    evidence: str


@dataclass
class EvalResult:
    eval_id: str
    eval_name: str
    exit_code: int
    timed_out: bool
    duration_seconds: float
    assertions: list[AssertionResult]
    output_dir: Path

    @property
    def pass_count(self) -> int:
        return sum(1 for assertion in self.assertions if assertion.passed)

    @property
    def total(self) -> int:
        return len(self.assertions)


def fail(message: str) -> None:
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_evals() -> dict:
    if not EVALS_JSON.is_file():
        fail(f"evals.json not found: {EVALS_JSON}")
    with EVALS_JSON.open("r", encoding="utf-8") as f:
        return json.load(f)


def read_skill_instructions() -> str:
    if not SKILL_MD.is_file():
        fail(f"SKILL.md not found: {SKILL_MD}")
    return SKILL_MD.read_text(encoding="utf-8")


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return slug or "eval"


def infer_workspace_name(eval_case: dict) -> str:
    for file_name in eval_case.get("files", []):
        normalized = file_name.replace("\\", "/")
        marker = "evals/files/"
        if marker not in normalized:
            continue
        rest = normalized.split(marker, 1)[1]
        return rest.split("/", 1)[0]
    fail(f"cannot infer workspace from eval-{eval_case.get('id')}")


def copy_fixture_workspace(workspace_name: str, output_dir: Path) -> Path:
    source = FIXTURES_DIR / workspace_name
    if not source.is_dir():
        fail(f"fixture workspace not found: {source}")

    temp_root = Path(tempfile.mkdtemp(prefix=f"propose-sync-{workspace_name}-"))
    workspace = temp_root / "workspace"
    shutil.copytree(source, workspace)

    spec = workspace / "spec.md"
    if spec.is_file():
        content = spec.read_text(encoding="utf-8")
        content = content.replace(
            f"propose-sync/evals/files/{workspace_name}/docs/propose/",
            "docs/propose/",
        )
        content = content.replace(
            f"propose-sync\\evals\\files\\{workspace_name}\\docs\\propose\\",
            "docs/propose/",
        )
        spec.write_text(content, encoding="utf-8")

    before = output_dir / "spec.before.md"
    if spec.is_file():
        before.write_text(spec.read_text(encoding="utf-8"), encoding="utf-8")

    return workspace


def detect_codex_command(workspace: Path, last_message: Path) -> list[str]:
    codex = shutil.which("codex")
    if not codex:
        fail("codex CLI not found; propose-sync eval runner requires codex exec")
    return [
        codex,
        "exec",
        "--dangerously-bypass-approvals-and-sandbox",
        "--skip-git-repo-check",
        "--cd",
        str(workspace),
        "--output-last-message",
        str(last_message),
        "-",
    ]


def build_prompt(skill_instructions: str, spec_path: Path) -> str:
    return f"""{skill_instructions}

---

Apply the above propose-sync skill instructions to this isolated eval workspace.

規格文檔路徑：{spec_path}

請直接執行 propose-sync：
- 讀取並更新上述規格文檔。
- 掃描目前工作區內的 `docs/propose/`。
- 不要等待使用者確認。
- 不要執行 git commit。
- 完成後輸出 propose-sync 完成摘要。
"""


def run_codex(command: list[str], prompt: str, output_file: Path, timeout: int) -> tuple[int, bool]:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    process = subprocess.Popen(
        command,
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
        strip_trailing_whitespace_file(output_file)
        return process.returncode, False
    except subprocess.TimeoutExpired as exc:
        process.kill()
        stdout, _ = process.communicate()
        partial = exc.output or stdout or ""
        output_file.write_text(f"{partial}\n[timeout] killed after {timeout}s\n", encoding="utf-8")
        strip_trailing_whitespace_file(output_file)
        return -1, True


def extract_completed_block(spec_text: str) -> str:
    match = re.search(r"(?ms)^## 已完成\s*\n(.*?)(?:^---\s*$|\Z)", spec_text)
    return match.group(0) if match else ""


def marker_contains(text: str, needle: str) -> bool:
    normalized = text.replace("\\", "/")
    candidate = needle.strip(" `。.")
    if candidate in normalized:
        return True
    return f"/{candidate}/" in normalized or f"`{candidate}" in normalized


def strip_trailing_whitespace_file(path: Path) -> None:
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8", errors="replace")
    cleaned = re.sub(r"[ \t]+(\r?\n)", r"\1", text)
    if cleaned != text:
        path.write_text(cleaned, encoding="utf-8")


def grade_assertion(assertion: dict, spec_text: str, completed_block: str, output_text: str) -> AssertionResult:
    name = assertion.get("name", "<unnamed>")
    check = assertion.get("check", "")

    passed = False
    evidence = "未匹配任何 deterministic grading rule"

    if "'## 已完成'" in check or "## 已完成" in name:
        passed = bool(completed_block)
        evidence = "spec.md contains ## 已完成" if passed else "spec.md missing ## 已完成"

    if "at or near the top" in check or "文檔頂部" in name:
        stripped = spec_text.lstrip()
        passed = stripped.startswith("## 已完成")
        evidence = "## 已完成 is at top" if passed else "## 已完成 is not at top"

    if "does NOT contain" in check:
        match = re.search(r"does NOT contain\s+(.+?)\s+folder path or\s+(.+)$", check)
        if match:
            folder = match.group(1).strip()
            label = match.group(2).strip()
            passed = not marker_contains(completed_block, folder) and label not in completed_block
            evidence = f"completed block excludes {folder}/{label}" if passed else f"completed block includes {folder} or {label}"

    elif "contains" in check and "folder path or" in check:
        match = re.search(r"contains\s+(.+?)\s+folder path or\s+(.+)$", check)
        if match:
            folder = match.group(1).strip()
            label = match.group(2).strip()
            passed = marker_contains(completed_block, folder) or label in completed_block
            evidence = f"completed block includes {folder}/{label}" if passed else f"completed block missing {folder}/{label}"

    if "output contains" in check:
        passed = "propose-sync 完成" in output_text or "已新增至 ## 已完成" in output_text
        evidence = "output contains completion summary" if passed else "output missing completion summary"

    if "original '## 報表匯出'" in check:
        passed = "## 報表匯出" in spec_text and "管理者可以匯出銷售報表" in spec_text
        evidence = "original report section preserved" if passed else "original report section missing"

    if "ui-complete" in check and ("treated as complete" in check or "resulting spec" in check):
        passed = marker_contains(completed_block, "ui-complete") or "Mobile Shell" in completed_block
        evidence = "ui-complete listed as complete" if passed else "ui-complete not listed"

    if "settings-complete is treated as complete" in check:
        passed = marker_contains(completed_block, "settings-complete") or "設定頁 Widget" in completed_block
        evidence = "settings-complete listed as complete" if passed else "settings-complete not listed"

    treated_match = re.search(r"treats\s+([a-z0-9-]+)\s+as complete", check)
    if treated_match:
        folder = treated_match.group(1)
        passed = marker_contains(completed_block, folder)
        evidence = f"{folder} listed as complete" if passed else f"{folder} not listed"

    return AssertionResult(name=name, passed=passed, evidence=evidence)


def write_diff(before: str, after: str, diff_file: Path) -> None:
    import difflib

    lines = difflib.unified_diff(
        before.splitlines(keepends=True),
        after.splitlines(keepends=True),
        fromfile="spec.before.md",
        tofile="spec.after.md",
    )
    diff_file.write_text("".join(lines), encoding="utf-8")


def display_path(path: Path) -> str:
    try:
        return path.relative_to(Path.cwd()).as_posix()
    except ValueError:
        return str(path)


def run_eval_case(eval_case: dict, skill_instructions: str, timeout: int) -> EvalResult:
    eval_id = str(eval_case.get("id", "unknown"))
    eval_name = eval_case.get("name") or f"eval-{eval_id}"
    case_dir = OUTPUT_DIR / f"eval-{eval_id}-{slugify(eval_name)}"

    if case_dir.exists():
        shutil.rmtree(case_dir)
    case_dir.mkdir(parents=True, exist_ok=True)

    workspace_name = infer_workspace_name(eval_case)
    workspace = copy_fixture_workspace(workspace_name, case_dir)
    temp_root = workspace.parent
    try:
        spec_path = workspace / "spec.md"
        output_file = case_dir / "output.txt"
        last_message = case_dir / "last-message.md"

        prompt = build_prompt(skill_instructions, spec_path)

        start = time.time()
        exit_code, timed_out = run_codex(
            detect_codex_command(workspace, last_message),
            prompt,
            output_file,
            timeout,
        )
        duration = time.time() - start

        strip_trailing_whitespace_file(spec_path)
        strip_trailing_whitespace_file(last_message)

        before_text = (case_dir / "spec.before.md").read_text(encoding="utf-8", errors="replace")
        after_text = spec_path.read_text(encoding="utf-8", errors="replace") if spec_path.exists() else ""
        (case_dir / "spec.after.md").write_text(after_text, encoding="utf-8")
        write_diff(before_text, after_text, case_dir / "diff.txt")
        strip_trailing_whitespace_file(case_dir / "spec.after.md")
        strip_trailing_whitespace_file(case_dir / "diff.txt")

        output_text = output_file.read_text(encoding="utf-8", errors="replace")
        if last_message.is_file():
            output_text += "\n" + last_message.read_text(encoding="utf-8", errors="replace")

        completed_block = extract_completed_block(after_text)
        assertions = [
            grade_assertion(assertion, after_text, completed_block, output_text)
            for assertion in eval_case.get("assertions", [])
        ]

        grading_lines = []
        for index, assertion in enumerate(assertions, 1):
            status = "PASS" if assertion.passed else "FAIL"
            grading_lines.append(f"E{index}: {status} - {assertion.name} - {assertion.evidence}")
        (case_dir / "grading.txt").write_text("\n".join(grading_lines) + "\n", encoding="utf-8")
        strip_trailing_whitespace_file(case_dir / "grading.txt")

        return EvalResult(
            eval_id=eval_id,
            eval_name=eval_name,
            exit_code=exit_code,
            timed_out=timed_out,
            duration_seconds=duration,
            assertions=assertions,
            output_dir=case_dir,
        )
    finally:
        if temp_root.name.startswith("propose-sync-"):
            shutil.rmtree(temp_root, ignore_errors=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run propose-sync BDD evals")
    parser.add_argument("eval_id", nargs="?", help="Optional eval id to run")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="Timeout per eval run in seconds")
    parser.add_argument("--jobs", type=int, default=0, help="Parallel jobs; default runs all selected evals in parallel")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data = load_evals()
    evals = data.get("evals", [])
    if args.eval_id:
        evals = [case for case in evals if str(case.get("id")) == args.eval_id]
    if not evals:
        print("No eval tasks to run.")
        return 0

    skill_instructions = read_skill_instructions()
    jobs = args.jobs if args.jobs > 0 else len(evals)
    jobs = max(1, min(jobs, len(evals)))

    print(f"=== {data.get('skill_name', 'propose-sync')} BDD evals ({len(evals)} total) ===")
    print(f"Launching {jobs} parallel run(s)...\n")

    results: list[EvalResult] = []
    with ThreadPoolExecutor(max_workers=jobs) as executor:
        futures = {
            executor.submit(run_eval_case, eval_case, skill_instructions, args.timeout): str(eval_case.get("id"))
            for eval_case in evals
        }
        for future in as_completed(futures):
            eval_id = futures[future]
            try:
                result = future.result()
            except Exception as exc:
                print(f"  [ERROR] eval-{eval_id}: {exc}")
                continue
            status = "TIMEOUT" if result.timed_out else ("OK" if result.exit_code == 0 else "FAIL")
            print(
                f"  [{status}] eval-{result.eval_id} {result.eval_name} "
                f"({result.duration_seconds:.1f}s) - {result.pass_count}/{result.total} passed"
            )
            results.append(result)

    print("\n=== Detailed Results ===")
    total_pass = 0
    total_assertions = 0
    for result in sorted(results, key=lambda item: int(item.eval_id) if item.eval_id.isdigit() else 0):
        print(f"\n[eval-{result.eval_id}] {result.eval_name} ({result.pass_count}/{result.total})")
        for index, assertion in enumerate(result.assertions, 1):
            status = "PASS" if assertion.passed else "FAIL"
            print(f"  {status} E{index}: {assertion.name}")
            print(f"       {assertion.evidence}")
        print(f"  artifacts: {result.output_dir}")
        total_pass += result.pass_count
        total_assertions += result.total

    summary = {
        "passed": total_pass,
        "total": total_assertions,
        "evals": [
            {
                "id": result.eval_id,
                "name": result.eval_name,
                "passed": result.pass_count,
                "total": result.total,
                "exit_code": result.exit_code,
                "timed_out": result.timed_out,
                "duration_seconds": result.duration_seconds,
                "output_dir": display_path(result.output_dir),
            }
            for result in sorted(results, key=lambda item: int(item.eval_id) if item.eval_id.isdigit() else 0)
        ],
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n=== Summary: {total_pass}/{total_assertions} assertions passed ===")
    print(f"Results saved to: {OUTPUT_DIR}")
    return 0 if total_pass == total_assertions and len(results) == len(evals) else 1


if __name__ == "__main__":
    if sys.platform == "win32" and not sys.flags.utf8_mode:
        import os

        env = os.environ.copy()
        env["PYTHONUTF8"] = "1"
        result = subprocess.run([sys.executable, "-X", "utf8", __file__] + sys.argv[1:], env=env)
        sys.exit(result.returncode)
    raise SystemExit(main())
