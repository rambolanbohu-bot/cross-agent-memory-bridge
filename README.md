# Cross-Agent Memory Bridge 1.0.0 — public repository, Release pending
[简体中文](README.zh-CN.md) · [Install](INSTALLATION.md) · [Compatibility](COMPATIBILITY.md) · [Privacy](PRIVACY.md) · [MIT License](LICENSE)

The Skill and local tools are completely free and open source under the MIT License. Local core operations do not require a paid API or forced subscription. Your chosen AI service may charge separately.

Local-first personal AI memory management through an Agent Skill, with explicit approval, privacy checks, shareable snapshots and version rollback.

The repository is public and MIT is confirmed: Copyright (c) 2026 Rambo. GitHub Release v1.0.0 has not been published yet. No user/download counts, certifications or success stories are invented.

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

Windows local behavior and the four-job GitHub Actions matrix (Windows/Ubuntu, Python 3.11/3.12) are evidenced. Linux/macOS complete installation and Claude, Gemini, Muse native integration remain NOT_TESTED; junction remains skipped. A real Codex chat explicitly loaded the skill and completed 26 CLI calls.

See CONTRIBUTING.md, GOVERNANCE.md, SECURITY.md and RELEASE_CHECKLIST.md. MIT is confirmed. Public repository visibility is active, while GitHub Release publication remains pending. No background installation or community-code execution; no automatic upload, commit, push or publication.

## License / 许可证
MIT License — Copyright (c) 2026 Rambo. [LICENSE_STATUS.md](LICENSE_STATUS.md) distinguishes confirmed licensing from the pending GitHub Release.
