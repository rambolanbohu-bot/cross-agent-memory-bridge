# Install / uninstall / 安装卸载
MIT is confirmed (Copyright (c) 2026 Rambo); public release actions remain unauthorized. Python 3.11+, no pip required. Review package code first. Verify SHA256SUMS.txt from a trusted source; hashes alone do not authenticate authorship. The source candidate includes tools/release_check.py for manifest/ZIP checks.

1. Verify ZIP with `python tools/release_check.py verify --archive FILE.zip`; extract only into a NEW staging directory outside any host discovery root. Reject traversal, absolute paths, links, duplicate/case-colliding members, unknown files and manifest mismatches.
2. Confirm requested version 1.0.0 against package manifest and retained reviewed ZIP/hash. There is no automatic latest-version installation.
3. Run V1 `upgrade --candidate EXTRACTED_SKILL --dry-run`; inspect scripts, permissions and hash. After approval use `upgrade --candidate EXTRACTED_SKILL --approve-sha256 HASH --install-to NEW_VERSION_DIRECTORY`. Existing destination must be refused.
4. Validate the complete copy before moving/renaming it to a NEW project .agents/skills/cross-agent-memory-bridge. Never overwrite an existing skill. Keep all other Skills, AGENTS.md and Codex configuration unchanged. Start the host normally to discover it; documented manual loading is a separate test.

V1 copy failure can leave partial staging files: do not activate them. Compare every remaining file to the trusted package. Unknown files, changed content, links or unclear paths require refusal/manual review. Delete only matching known files and empty directories, then retry in a clean directory. Never recursively delete a guessed workspace path. Do not install directly into active discovery before a full copy verifies.

Uninstall only the exact installed directory after path, manifest and hash validation. Preserve the parent skills directory, other skills, configuration and user vault (which must be outside the skill). Unexpected user-created files cause refusal, not deletion. Retaining reviewed version directories permits deliberate code rollback; profile rollback is a separate approved command.

本轮在中文及空格路径验证全新/指定版本安装、防覆盖、复制失败恢复和清单式卸载。原 V1 upgrade 不是事务式安装器，因此使用发现目录外的分期安装；不确定、未知文件和权限失败均停止，禁止降级系统限制。
