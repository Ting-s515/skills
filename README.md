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

## Skill Index

Private-only skills are intentionally omitted from this public index.

| Skill | Purpose | Use When |
| --- | --- | --- |
| [`ac-to-test`](ac-to-test/) | Converts acceptance criteria into red-test skeletons. | You have an `AC.md` or Given/When/Then criteria and want test boundaries before implementation. |
| [`apply`](apply/) | Implements a prepared proposal with a test-first workflow. | You have a `docs/propose/...` feature folder and want to start or continue implementation. |
| [`bdd-unit-test`](bdd-unit-test/) | Adds BDD-style unit tests for existing code. | You need focused happy-path, edge-case, and error-case tests for target files. |
| [`clarify-flow`](clarify-flow/) | Rewrites messy business flows into precise structured steps. | Requirements contain unclear branches, loops, or mixed decision logic. |
| [`code-reviewer`](code-reviewer/) | Reviews code changes against business requirements. | You need to verify whether an implementation matches a spec or user story. |
| [`explaining-code`](explaining-code/) | Explains code, tools, or architecture with structured diagrams. | You need a clear walkthrough of how something works. |
| [`export-ac`](export-ac/) | Produces an `AC.md` acceptance-criteria document. | You explicitly want to create acceptance criteria before implementation. |
| [`export-conversation`](export-conversation/) | Exports the current conversation into Markdown. | You need to preserve context for another model or session. |
| [`export-feature-file`](export-feature-file/) | Converts behavior specs into executable `.feature` files. | You need framework-ready Gherkin for Cucumber, Behave, Reqnroll, or similar tools. |
| [`export-gherkin`](export-gherkin/) | Converts requirements or logic into human-readable Gherkin. | You need Given/When/Then specs for stakeholder alignment, not executable test files. |
| [`fleet-review`](fleet-review/) | Runs multi-agent review for cross-model validation. | You explicitly request `fleet-review` with a spec path. |
| [`llm-repo`](llm-repo/) | Loads relevant pages from a local LLM knowledge base. | You want an answer grounded in the local `wiki/` repository. |
| [`llm-repo-raw-capture`](llm-repo-raw-capture/) | Saves deep-search findings as local raw knowledge snapshots. | You need traceable web-search notes for later wiki ingestion. |
| [`plan-doc`](plan-doc/) | Creates implementation plan documents from code and requirements. | You need a `*.plan.md` spec that another agent can implement. |
| [`propose`](propose/) | Turns requirements into clarified specs, Gherkin, and tasks. | You want to plan a feature or route bug fixes before implementation. |
| [`propose-sync`](propose-sync/) | Syncs completed proposal status back to requirement documents. | You need completed `docs/propose/` work reflected in the source spec. |
| [`react-design`](react-design/) | Guides React component, hook, service, and state design. | You are building or refactoring React code and need architecture guardrails. |
| [`remove-nul`](remove-nul/) | Removes Windows reserved-name files that normal tools cannot delete. | `git status` shows files such as `nul`, `con`, or `aux`. |
| [`req-interview`](req-interview/) | Runs an interactive requirement or architecture interview. | You want edge cases, missing scenarios, or design options discussed to convergence. |
| [`search-local-skill`](search-local-skill/) | Searches local skill directories and descriptions. | You need to list, find, or browse available local skills. |
| [`skill-creator-plus`](skill-creator-plus/) | Creates, improves, and evaluates skills. | You want to build a new skill, refine an existing one, or benchmark skill behavior. |
| [`slim-doc`](slim-doc/) | Compresses existing Markdown specs by removing implementation detail. | You need a shorter document that keeps APIs, diagrams, and key structures. |
| [`web-search`](web-search/) | Enforces up-to-date web research for time-sensitive questions. | A question involves current versions, news, prices, policies, or recent facts. |
| [`writing-blog-post`](writing-blog-post/) | Drafts structured Markdown blog posts. | You explicitly want content written or reorganized as a blog article. |
| [`writing-markdown`](writing-markdown/) | Produces structured Markdown technical documents. | You need technical notes, design docs, diagrams, or process documentation. |
| [`writing-training-doc`](writing-training-doc/) | Creates hands-on technical training material. | You need lab guides, SOPs, onboarding docs, or practical course content. |

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
