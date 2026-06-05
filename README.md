# Ting-s515 Skills

Personal AI agent skills and workflow instructions maintained by Ting-s515.

This repository is a public skill library for reusable agent behaviors such as requirement planning, BDD test generation, code review, documentation workflows, local knowledge-base lookup, and web-search capture.

For Traditional Chinese documentation, see [README.zh-TW.md](README.zh-TW.md).

## Repository Layout

- `*/SKILL.md` - the entrypoint for each skill.
- `*/scripts/` - optional helper scripts used by a skill.
- `*/references/`, `*/templates/`, `*/examples/` - optional supporting material loaded only when needed.
- `AGENTS.md` - Codex-facing project rules.
- `CLAUDE.md` - Claude-facing project rules.

## Skill Groups

- Planning and implementation workflows: `propose`, `apply`, `propose-sync`, `plan-doc`, `req-interview`.
- BDD and acceptance criteria: `export-ac`, `export-gherkin`, `export-feature-file`, `ac-to-test`, `bdd-unit-test`.
- Review and analysis: `code-reviewer`, `fleet-review`, `explaining-code`, `react-design`.
- Documentation and writing: `slim-doc`, `clarify-flow`, `writing-training-doc`, `writing-markdown`, `writing-blog-post`.
- Knowledge and research support: `llm-repo`, `llm-repo-raw-capture`, `web-search`.
- Utility and maintenance: `export-conversation`, `pff`, `skill-creator-plus`, `search-local-skill`, `remove-nul`.

## Usage

Each skill is designed to be read from its own directory. Start with the target skill's `SKILL.md`, then load referenced files only when the skill asks for them.

When using these skills in another agent environment:

1. Copy the needed skill directory.
2. Keep the directory structure intact.
3. Preserve the `SKILL.md` frontmatter.
4. Review any scripts before running them in your environment.

## License

This repository is licensed under the [MIT License](LICENSE).

You may use, copy, modify, distribute, and sublicense the content under the MIT terms. Keep the copyright notice and license text.
