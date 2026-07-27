#!/usr/bin/env python3
"""檢查 skill 路徑是否可在 Windows 與 macOS 的不同 filesystem 規則下使用。"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
EXCLUDED_DIRECTORY_NAMES = {
    ".git",
    "eval-results",
    "eval-results-bdd",
    "fixtures",
    "node_modules",
}
TEXT_SUFFIXES = {
    "",
    ".cjs",
    ".css",
    ".html",
    ".js",
    ".json",
    ".md",
    ".mjs",
    ".py",
    ".sh",
    ".ts",
    ".tsx",
    ".txt",
    ".yaml",
    ".yml",
}
ESCAPE_ONLY_RELATIVE_MATCHES = {
    r".\0",
    r".\b",
    r".\f",
    r".\n",
    r".\r",
    r".\t",
    r".\v",
}
INTENTIONAL_PLATFORM_MATCHES = {
    # 這個完整 match 必須展示 Windows 保留裝置路徑，否則無法說明故障原因。
    ("remove-nul/SKILL.md", "Windows drive-letter 絕對路徑"): (r"C:\...\nul",),
}


@dataclass(frozen=True)
class Finding:
    skill: str
    path: str
    line: int
    message: str


def is_excluded(path: Path) -> bool:
    return any(part in EXCLUDED_DIRECTORY_NAMES for part in path.parts)


def discover_skill_entries(root: Path) -> list[Path]:
    # 大小寫不敏感探索才能在 Windows 上抓到會於 macOS 失效的 SKILL.MD。
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file()
        and path.name.casefold() == "skill.md"
        and not is_excluded(path.relative_to(root))
    )


def filesystem_entry_case_findings(root: Path, entries: list[Path]) -> list[Finding]:
    return [
        Finding(
            entry.parent.relative_to(root).as_posix(),
            entry.relative_to(root).as_posix(),
            0,
            "入口檔必須精確命名為 SKILL.md",
        )
        for entry in entries
        if entry.name != "SKILL.md"
    ]


def tracked_entry_case_findings(root: Path) -> list[Finding]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        return [Finding("repository", ".", 0, "無法讀取 git index 以驗證入口檔名大小寫")]

    findings: list[Finding] = []
    for raw_path in result.stdout.split("\0"):
        if not raw_path:
            continue
        name = Path(raw_path).name
        if name.casefold() == "skill.md" and name != "SKILL.md":
            skill = Path(raw_path).parent.as_posix()
            findings.append(
                Finding(skill, Path(raw_path).as_posix(), 0, "入口檔必須精確命名為 SKILL.md")
            )
    return findings


def iter_operational_files(skill_root: Path) -> list[Path]:
    return sorted(
        path
        for path in skill_root.rglob("*")
        if path.is_file()
        and path.suffix.lower() in TEXT_SUFFIXES
        and not is_excluded(path.relative_to(skill_root))
    )


def path_findings(root: Path, entries: list[Path]) -> list[Finding]:
    patterns = (
        (
            re.compile(r"(?i)(?<![a-z])[a-z]:[\\/][^\s`|'\"<>]*"),
            "Windows drive-letter 絕對路徑",
            False,
        ),
        (re.compile(r"(?i)/mnt/[a-z]/Users/"), "WSL 專屬使用者路徑", False),
        (
            re.compile(r"/(?:Users|home)/[^/<>'\"`\s]+/"),
            "硬編碼 Unix 使用者 home 路徑",
            False,
        ),
        (
            re.compile(r"~[\\/]\.claude[\\/]skills[\\/]"),
            "假設 skill 固定安裝在 ~/.claude/skills",
            False,
        ),
        (
            re.compile(r"(?<![A-Za-z0-9_.\\])\.\.?\\(?!\\)[^\s`|'\"<>\\]+"),
            "Windows 相對路徑分隔符",
            False,
        ),
        (
            re.compile(
                r"(?i)(?<![A-Za-z0-9_\\])"
                r"(?:assets|docs|evals|examples|references|scripts|src|templates|test|tests)"
                r"\\(?!\\)[^\s`|'\"<>\\]+"
            ),
            "Windows 相對路徑分隔符",
            True,
        ),
    )
    findings: list[Finding] = []

    for entry in entries:
        skill_root = entry.parent
        skill_name = skill_root.relative_to(root).as_posix()
        for path in iter_operational_files(skill_root):
            relative_path = path.relative_to(root).as_posix()
            content = path.read_text(encoding="utf-8", errors="replace")
            for line_number, line in enumerate(content.splitlines(), start=1):
                for pattern, message, markdown_only in patterns:
                    if markdown_only and path.suffix.lower() != ".md":
                        continue
                    for match in pattern.finditer(line):
                        matched_text = match.group(0)
                        prefix = line[: match.start()]
                        suffix = line[match.end() :]
                        is_raw_string = bool(re.search(r"(?i)r['\"]$", prefix))
                        if (
                            message == "Windows 相對路徑分隔符"
                            and matched_text in ESCAPE_ONLY_RELATIVE_MATCHES
                            and not is_raw_string
                            and not suffix.startswith("\\")
                        ):
                            continue
                        allowed_matches = INTENTIONAL_PLATFORM_MATCHES.get(
                            (relative_path, message), ()
                        )
                        if matched_text in allowed_matches:
                            continue
                        findings.append(Finding(skill_name, relative_path, line_number, message))
                if "$env:USERPROFILE" in line and not ("macOS" in line and "$HOME" in line):
                    findings.append(
                        Finding(skill_name, relative_path, line_number, "只使用 Windows USERPROFILE 定位路徑")
                    )
    return findings


def main() -> int:
    entries = discover_skill_entries(REPOSITORY_ROOT)
    findings = filesystem_entry_case_findings(REPOSITORY_ROOT, entries)
    findings.extend(tracked_entry_case_findings(REPOSITORY_ROOT))
    findings.extend(path_findings(REPOSITORY_ROOT, entries))

    findings_by_skill: dict[str, list[Finding]] = {}
    for finding in findings:
        findings_by_skill.setdefault(finding.skill, []).append(finding)

    for entry in entries:
        skill = entry.parent.relative_to(REPOSITORY_ROOT).as_posix()
        skill_findings = findings_by_skill.get(skill, [])
        if not skill_findings:
            print(f"PASS {skill}")
            continue
        print(f"FAIL {skill}")
        for finding in skill_findings:
            location = f"{finding.path}:{finding.line}" if finding.line else finding.path
            print(f"  {location} - {finding.message}")

    repository_findings = findings_by_skill.get("repository", [])
    for finding in repository_findings:
        print(f"FAIL repository - {finding.message}")

    failed_skills = {item.skill for item in findings if item.skill != "repository"}
    print(f"Summary: {len(entries) - len(failed_skills)}/{len(entries)} skills passed")
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
