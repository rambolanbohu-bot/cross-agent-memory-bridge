# Cross-Agent Memory Bridge 1.0.0 — Public 仓库，Release 待发布
[English](README.md) · [安装卸载](INSTALLATION.md) · [兼容](COMPATIBILITY.md) · [隐私](PRIVACY.md) · [MIT 许可证](LICENSE)

Skill 与本地工具完全免费、按 MIT 开源。本地核心功能不依赖付费 API 或强制订阅；用户自选的 AI 服务可能另外收费。

基于 Agent Skill 的本地优先个人 AI 档案管理：明确审批、隐私检查、可分享快照及版本回滚。

仓库已经公开，MIT 许可证已正式确认：Copyright (c) 2026 Rambo。GitHub Release v1.0.0 尚未发布。无虚构用户量、下载量、成功案例或外部认证。

Python 3.11+ 标准库；Git 仅用于可选暂存区扫描。核心无需服务器、数据库服务、遥测、强制订阅或付费 API；用户自选模型费用另计。
```text
python skills/cross-agent-memory-bridge/scripts/memory_bridge.py init --output 源码工程之外的全新目录
python skills/cross-agent-memory-bridge/scripts/memory_bridge.py validate --path 档案目录
python skills/cross-agent-memory-bridge/scripts/memory_bridge.py read --path 档案目录
python skills/cross-agent-memory-bridge/scripts/memory_bridge.py privacy-check --path 档案目录
```
路径含空格须加引号，使用绝对路径或简单子目录；安全检查拒绝含上级穿越段的路径。初始化不采集系统身份、聊天或其他项目资料，所有字段自愿。中文完整操作见 docs/CLI.zh-CN.md，审批示例见 docs/SELF_TEST.md。

profile.json 保存稳定 ID、来源、日期、状态和版本；pending 不是 confirmed。默认只读取或导出已确认、可分享、非敏感记录。修改经提案、差异、具体内容与哈希审批、review/apply；导出先预览再批准；回滚形成新版本并保留审计。

GitHub 仓库不是自动同步服务，不支持所有 AI 自动双向永久记忆。ChatGPT/Claude/Gemini 等可能需要手工导入与刷新快照。私人资料默认不得混入跨平台导出。正则不能代替人工语义审核；哈希不是签名，批准文件不是身份认证。没有自动上传、提交、推送、建库或后台执行社区代码。

Windows/Python 3.12.10、本项目GitHub Actions四项矩阵（Windows/Ubuntu、Python 3.11/3.12）已有证据。Linux/macOS完整安装、Claude/Gemini/Muse原生集成仍未真实验收；junction 保持跳过。真实 Codex 聊天显式加载并执行26次CLI。

贡献及治理见 CONTRIBUTING.md/GOVERNANCE.md/SECURITY.md，发布门禁见 RELEASE_CHECKLIST.md。MIT 已确认；仓库已公开，但GitHub Release v1.0.0仍待发布。版本升级和回退由用户自主选择，正式Release需另行批准。

## License / 许可证
MIT License — Copyright (c) 2026 Rambo. [LICENSE_STATUS.md](LICENSE_STATUS.md) 区分已确认许可与待发布GitHub Release。
