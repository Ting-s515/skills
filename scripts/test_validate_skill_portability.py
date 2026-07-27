from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from validate_skill_portability import (
    discover_skill_entries,
    filesystem_entry_case_findings,
    path_findings,
)


class ValidateSkillPortabilityTest(unittest.TestCase):
    def create_skill(self, root: Path, entry_name: str, content: str) -> Path:
        skill_root = root / "sample-skill"
        skill_root.mkdir()
        entry = skill_root / entry_name
        entry.write_text(content, encoding="utf-8")
        return entry

    def test_untracked_uppercase_entry_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.create_skill(root, "SKILL.MD", "---\nname: sample-skill\n---\n")

            entries = discover_skill_entries(root)
            findings = filesystem_entry_case_findings(root, entries)

            self.assertEqual(1, len(findings))
            self.assertIn("SKILL.md", findings[0].message)

    def test_windows_relative_path_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.create_skill(
                root,
                "SKILL.md",
                "```powershell\nnpm --prefix .\\docs-web test\n```\n",
            )

            findings = path_findings(root, discover_skill_entries(root))

            self.assertTrue(any(item.message == "Windows 相對路徑分隔符" for item in findings))

    def test_posix_relative_path_is_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.create_skill(
                root,
                "SKILL.md",
                "```shell\nnpm --prefix ./docs-web test\n```\n",
            )

            findings = path_findings(root, discover_skill_entries(root))

            self.assertEqual([], findings)

    def test_python_escape_sequence_is_not_a_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.create_skill(
                root,
                "SKILL.md",
                '```python\nmessage = "Complete.\\n"\n```\n',
            )

            findings = path_findings(root, discover_skill_entries(root))

            self.assertEqual([], findings)

    def test_common_windows_relative_path_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.create_skill(root, "SKILL.md", "讀取 `docs\\guide.md`。\n")

            findings = path_findings(root, discover_skill_entries(root))

            self.assertTrue(any(item.message == "Windows 相對路徑分隔符" for item in findings))

    def test_raw_windows_path_inside_python_fence_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.create_skill(
                root,
                "SKILL.md",
                '```python\npath = r".\\docs"\n```\n',
            )

            findings = path_findings(root, discover_skill_entries(root))

            self.assertTrue(any(item.message == "Windows 相對路徑分隔符" for item in findings))

    def test_mixed_fence_markers_do_not_turn_escape_into_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.create_skill(
                root,
                "SKILL.md",
                '```python\n~~~\nmessage = "Complete.\\n"\n```\n',
            )

            findings = path_findings(root, discover_skill_entries(root))

            self.assertEqual([], findings)

    def test_escape_followed_by_text_is_not_a_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.create_skill(
                root,
                "SKILL.md",
                '```python\nmessage = "Complete.\\nNext"\n```\n',
            )

            findings = path_findings(root, discover_skill_entries(root))

            self.assertEqual([], findings)

    def test_path_segment_named_n_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.create_skill(root, "SKILL.md", "執行 `.\\n\\build.py`。\n")

            findings = path_findings(root, discover_skill_entries(root))

            self.assertTrue(any(item.message == "Windows 相對路徑分隔符" for item in findings))

    def test_standard_resource_directories_with_backslashes_are_rejected(self) -> None:
        for relative_path in ("examples\\sample.md", "templates\\report.md"):
            with self.subTest(relative_path=relative_path):
                with tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    self.create_skill(root, "SKILL.md", f"讀取 `{relative_path}`。\n")

                    findings = path_findings(root, discover_skill_entries(root))

                    self.assertTrue(
                        any(item.message == "Windows 相對路徑分隔符" for item in findings)
                    )

    def test_raw_string_escape_name_is_rejected_as_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.create_skill(
                root,
                "SKILL.md",
                '```python\npath = r".\\n"\n```\n',
            )

            findings = path_findings(root, discover_skill_entries(root))

            self.assertTrue(any(item.message == "Windows 相對路徑分隔符" for item in findings))

    def test_remove_nul_exception_does_not_hide_user_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill_root = root / "remove-nul"
            skill_root.mkdir()
            (skill_root / "SKILL.md").write_text(
                '| `cmd /c "del \\\\?\\C:\\...\\nul"` | Windows 範例 | '
                "`C:\\Users\\someone\\secret.txt`\n",
                encoding="utf-8",
            )

            findings = path_findings(root, discover_skill_entries(root))

            self.assertEqual(1, len(findings))
            self.assertEqual("Windows drive-letter 絕對路徑", findings[0].message)


if __name__ == "__main__":
    unittest.main()
