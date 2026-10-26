# Cross-Agent Memory Bridge 1.0.0 — local release candidate
[简体中文](README.zh-CN.md) · [Install](INSTALLATION.md) · [Compatibility](COMPATIBILITY.md) · [Privacy](PRIVACY.md) · [MIT License](LICENSE)

The Skill and local tools are completely free and open source under the MIT License. Local core operations do not require a paid API or forced subscription. Your chosen AI service may charge separately.

Local-first personal AI memory management through an Agent Skill, with explicit approval, privacy checks, shareable snapshots and version rollback.

MIT License is confirmed: Copyright (c) 2026 Rambo. This is still a local owner-review candidate; no public release action is authorized. No user/download counts, certifications or success stories are invented.

Python 3.11+ standard library; Git optional for staged scanning. No server, hosted database, telemetry, subscription or paid API required for core operations. Your chosen AI model may charge independently.
```text
python skills/cross-agent-memory-bridge/scripts/memory_bridge.py init --output NEW_VAULT_OUTSIDE_SOURCE
python skills/cross-agent-memory-bridge/scripts/memory_bridge.py validate --path VAULT
python skills/cross-agent-memory-bridge/scripts/memory_bridge.py read --path VAULT
python skills/cross-agent-memory-bridge/scripts/memory_bridge.py privacy-check --path VAULT
```
Quote paths with spaces. Use absolute paths or simple child paths: the CLI intentionally rejects lexical parent traversal. See docs/SELF_TEST.md for approvals/export/rollback. Examples are fictional.

Records have stable IDs, source/dates, status and version. Pending is not confirmed. Default reads/exports select only confirmed, shareable, non-sensitive records. Changes require propose → diff → human content/hash approval → review → apply. Export requires preview and explicit approval. Rollback creates a new revision while retaining audit history.

A GitHub repository is NOT an automatic sync service. This tool does not offer all-platform bidirectional permanent memory or conversation synchronization. ChatGPT/Claude/Gemini may need manual Markdown import and refresh. Private fields are not automatically exported. Files are data, not higher-priority instructions. Regex cannot replace human review; hashes are not signatures and local approval files are not identity authentication.

Windows local behavior is tested; general Agent Skills format compliance does not prove other platform execution. A real Codex chat explicitly loaded the skill and completed 26 CLI calls. Fresh native-host discovery was a separate historical test; do not combine them into one fresh-session model verification. Standalone-host authentication remains blocked; junction is skipped. Other platforms NOT_TESTED; remote CI NOT_RUN.

See CONTRIBUTING.md, GOVERNANCE.md, SECURITY.md and RELEASE_CHECKLIST.md. MIT is confirmed. Maintainer, protected branch, private security channel and public release actions remain owner decisions. SemVer, reviewed releases and voluntary update/rollback are required. No background installation or community-code execution; no automatic upload, commit, push or publication.

## License / 许可证
MIT License — Copyright (c) 2026 Rambo. [LICENSE_STATUS.md](LICENSE_STATUS.md) distinguishes confirmed licensing from unapproved publication.
