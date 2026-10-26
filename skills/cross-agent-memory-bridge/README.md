# Cross-Agent Memory Bridge 1.0.0
MIT License — Copyright (c) 2026 Rambo. License is confirmed; public release actions are NOT authorized. See LICENSE and LICENSE_STATUS.md. No legal name or company is used.

Python 3.11+ standard library; optional Git for staged scans. Install only a reviewed complete unit in a NEW project .agents/skills/cross-agent-memory-bridge directory after staging, hash validation and user consent. Never overwrite an existing Skill or edit global settings. Keep personal vaults outside this unit so uninstall cannot remove them.

From this skill directory: `python scripts/memory_bridge.py init --output NEW_VAULT_OUTSIDE_SKILL`, then validate/read/privacy-check with --path VAULT. Changes use propose/diff/review/apply with human approval. Export uses preview and exact hash approval; rollback creates a new revision. Full workflow details are in references/APPROVAL_AND_ROLLBACK.md.

本包为 1.0.0，MIT 已确认，版权公开署名 Rambo（2026）。许可证不等于用户批准代理发布。私人档案另存；先审核后安装，不改全局配置。仅已确认、可分享、非敏感记录进入跨 AI 快照，pending/private 默认排除。未测试的平台不能当作已集成。
