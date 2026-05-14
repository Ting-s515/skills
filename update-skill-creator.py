#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


REPO_URL = "https://github.com/anthropics/claude-plugins-official.git"
SKILL_PATH = Path("plugins/skill-creator/skills/skill-creator")
TARGET_DIR = Path.home() / ".claude" / "skills" / "skill-creator"
PROTECTED_ITEMS = ["agents", "assets", "eval-viewer", "references", "scripts", "LICENSE.txt", "SKILL.md"]
ANCHOR = "references/schemas.md` for the full schema"


def fail(message: str) -> None:
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(1)


def run(command: list[str], cwd: Path | None = None) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def copy_children(source: Path, target: Path) -> None:
    target.mkdir(parents=True, exist_ok=True)
    for item in source.iterdir():
        destination = target / item.name
        if item.is_dir():
            shutil.copytree(item, destination, dirs_exist_ok=True)
        else:
            shutil.copy2(item, destination)


def remove_target_items() -> None:
    for item_name in PROTECTED_ITEMS:
        path = TARGET_DIR / item_name
        if path.is_dir():
            shutil.rmtree(path)
        elif path.exists():
            path.unlink()


def extract_local_extension(local_ext: Path) -> str:
    lines = local_ext.read_text(encoding="utf-8").splitlines()
    try:
        start = lines.index("## 插入內容") + 1
    except ValueError:
        fail("找不到 local_extensions.md 的「## 插入內容」區塊，無法套用本地擴充。")

    insert_content = "\n".join(lines[start:]).strip("\n")
    if not insert_content.strip():
        fail("local_extensions.md 的「## 插入內容」區塊沒有可插入內容，無法套用本地擴充。")
    return insert_content


def apply_local_extension() -> None:
    local_ext = TARGET_DIR / "evals" / "local_extensions.md"
    if not local_ext.is_file():
        return

    skill_md = TARGET_DIR / "SKILL.md"
    insert_content = extract_local_extension(local_ext)
    skill_content = skill_md.read_text(encoding="utf-8")
    anchor_index = skill_content.find(ANCHOR)
    if anchor_index < 0:
        fail(f"找不到 SKILL.md 錨點：{ANCHOR}，無法套用本地擴充。")

    end_of_line = skill_content.find("\n", anchor_index)
    if end_of_line < 0:
        end_of_line = len(skill_content)

    updated = skill_content[: end_of_line + 1] + insert_content + "\n" + skill_content[end_of_line + 1 :]
    skill_md.write_text(updated, encoding="utf-8", newline="\n")

    checks = {
        "evals/run_evals.py": "本地擴充未成功插入 SKILL.md。",
        "本地規則：Codex eval runner": "本地擴充缺少 Codex eval runner 本地規則。",
        "--dangerously-bypass-approvals-and-sandbox": "本地擴充缺少 Codex bypass sandbox 參數。",
    }
    for pattern, message in checks.items():
        if pattern not in updated:
            fail(message)

    print(">>> 已套用本地擴充 (local_extensions.md)")


def main() -> int:
    print(">>> 拉取最新 skill-creator...")
    with tempfile.TemporaryDirectory() as temp_dir, tempfile.TemporaryDirectory() as evals_backup_dir:
        temp_path = Path(temp_dir)
        evals_backup = Path(evals_backup_dir)

        run(["git", "clone", "--depth=1", "--filter=blob:none", "--sparse", REPO_URL, str(temp_path), "--quiet"])
        run(["git", "sparse-checkout", "set", str(SKILL_PATH).replace("\\", "/")], cwd=temp_path)

        print(f">>> 覆蓋本地 {TARGET_DIR} ...")
        evals_dir = TARGET_DIR / "evals"
        if evals_dir.is_dir():
            copy_children(evals_dir, evals_backup)

        remove_target_items()
        copy_children(temp_path / SKILL_PATH, TARGET_DIR)

        if evals_dir.exists():
            shutil.rmtree(evals_dir)
        (evals_dir / "files").mkdir(parents=True, exist_ok=True)
        if any(evals_backup.iterdir()):
            copy_children(evals_backup, evals_dir)

    apply_local_extension()
    print(">>> 完成！skill-creator 已更新至最新版本。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
