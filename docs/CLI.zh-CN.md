# 中文操作手册
本工具需要 Python 3.11+，核心仅标准库，无需 pip 安装、API Key 或服务器。Git 仅用于可选的暂存区扫描。全部操作默认本地，不创建远程仓库，不提交、推送或上传。

## 初始化和读取
在项目目录运行 `python skills/cross-agent-memory-bridge/scripts/memory_bridge.py`，下文用 `CLI` 简称这段命令。`CLI init --output 目录` 只接受不存在的新目录；生成空白档案及说明文件。可跳过所有资料问题，不从系统或其他项目搜集身份。私人目录应放在开源工程之外。`CLI validate --path 目录` 验证结构；`CLI status --path 目录` 返回版本和哈希；`CLI read --path 目录` 只返回已确认、可分享且非敏感记录，并另报待确认数量。版本及内容哈希不变，才是同一份档案。Markdown 笔记不自动成为事实，profile.json 才是事实来源。

## 记录结构和更新
每条记录必须完整给出 id、text、source、created_at、verified_at、status、tags、visibility、sensitive、version。ID 稳定且唯一；日期使用 ISO 日期。来源可为 user/document/agent-proposal/synthetic。状态可为 confirmed/pending/superseded；已确认必须有验证日期。visibility 使用 private 或 shareable，敏感开关必须为布尔值。新记录版本从 1 开始，纠错时递增一。重复事实、重复 ID、重复 JSON 键、未知字段和冲突均拒绝，不自动合并。

change.json 包含 why（原因）、source（来源）、operations（操作）。upsert 提供完整 record；revoke 提供 id，将记录标为 superseded。可参考 examples/fictional-change.json，示例全部虚构。

`CLI propose --path 目录 --change change.json --out proposal.json` 生成 24 小时有效提案，不改档案。`CLI diff --path 目录 --proposal proposal.json` 显示记录 ID 和哈希差异。审核者必须在本地打开提案，检查每条具体内容、来源、原因、状态与分享设置，不能只看哈希。用户明确批准准确 proposal_sha256 后，才运行 `CLI review --path 目录 --proposal proposal.json --reviewer 审核者 --approve-sha256 提案哈希 --out approval.json`，再运行 `CLI apply --path 目录 --proposal proposal.json --approval approval.json`。AI 不得自批真实事实。

apply 检查提案内容、基础版本、基础哈希、批准及有效期。竞争修改、过期或被改动的提案都会被拒绝；需重新提案并审批。写入前保存版本备份，再原子替换当前文件。审计记录原因、来源、审核者、时间和哈希，不在公共日志输出原始事实。why 或审核者名称也可能敏感，整个档案及其历史必须私有。若异常留下未生效备份或锁，确认没有进程运行后再人工处理，不能自动删除锁。

## 隐私检测和导出
`CLI privacy-check --path 目录` 检查疑似认证、身份、银行、客户、联系方式等风险，仅报告类别、位置及行号，不回显匹配值。支持 UTF-8/BOM 和 UTF-16；拒绝二进制或未知编码、超过 1 MiB 文件、过多条目、符号链接和 Windows 重解析点。隐藏目录报告但不批量遍历。加 `--staged` 时读取 Git 暂存 blob，而非只读工作区。`CLI inspect-archive --archive 文件.zip` 只检查，不解压，拒绝路径穿越、绝对路径、链接和大小预算超限。正则无法识别所有语义隐私、混淆和拆分，必须人工审核，不能把 CLEAN 当作分享授权。

`CLI export --path 目录 --target generic --out 已审核.md --preview` 只预览数量、来源、排除项与 export_sha256，不产生导出文件。用 read 审核入选事实，并确认接收者和用途。用户明确批准后，再运行同一命令去掉 --preview，加 `--approve-sha256 导出哈希`。目标可用 generic/codex/muse/claude-code/gemini-cli/cursor/opencode/copilot；目前只是同一开放格式加目标标签，不代表平台实测成功。文件输出在档案目录外，不会自动上传。

## 快照与刷新
快照包含结构版本、本地版本、来源哈希、选定事实、生成时间和内容哈希。`CLI verify-snapshot --snapshot 文件 --path 当前档案` 会比对当前档案与快照内容，不一致显示 STALE。只给 `--expected-sha256 已单独可信获取的来源哈希` 时，一致仅显示 SOURCE_HASH_MATCH_UNAUTHENTICATED，不能证明快照事实未被伪造；不提供参考来源时显示 UNKNOWN_FRESHNESS。哈希不是作者签名，生成时间不在内容哈希保护内。没有任何远程实时同步。

普通聊天产品可手工上传单文件快照，需先审批内容和接收者。接收 Agent 应返回 version、content_sha256、source、loaded_files、loaded_at、verified_or_snapshot，并明确这是快照。刷新需要重新导出和审批，旧文件不自动变化。

## 历史和回滚
`CLI history --path 目录` 查看审计，`CLI status` 得到当前 content_sha256。先检查要恢复的本地版本，再运行 `CLI rollback --path 目录 --version 旧版本号 --approve-sha256 当前内容哈希`。恢复会创建新版本，保留审计，不删除历史。因此旧快照仍可识别为过期。永久删除敏感信息需要用户另行处理所有历史和外部副本。`CLI migrate --path 目录 --to-schema 1.0 --dry-run` 是已验证的无变化操作；目前不支持其他结构迁移，拒绝假装升级为不存在的格式。

## 社区升级和回退
采用 MAJOR.MINOR.PATCH：破坏性变更增加主版本，兼容功能增加次版本，修复增加补丁版本。结构变更必须附可逆迁移与测试，安装技能不能自动迁移私人档案。

`CLI check-updates` 默认 OFFLINE；只有明确选择 `--online --repo OWNER/REPO` 才读取 GitHub 最新 Release 元数据，不收集令牌、不下载代码。状态区分 OFFLINE、NO_AUTH、API_LIMIT 和 PRIVATE_REPO_OR_NOT_FOUND；未授权时无法区分私有与不存在。显示可用哈希，签名仍标 NOT_VERIFIED。

手工获得候选包后，运行 `CLI upgrade --candidate 目录 --dry-run`，审核文件/脚本差异、哈希、权限和迁移说明。确认后用 `--approve-sha256 候选哈希 --install-to 全新目录` 复制完整技能，不覆盖活动安装，不执行候选代码。用户主动选择新目录并记录版本；保留旧目录即可回退。失败的部分复制不会自动启用，需人工检查。禁止后台安装或执行社区提交代码。

## 安全边界和社区维护
本工具不加密数据，Windows chmod 也不等于目录 ACL。审批文件是本地流程证据，不是身份认证；恶意程序若有不受限写权限可绕过，需宿主授权及操作系统权限限制。便携路径检查不能完全消除恶意同用户进程替换文件的竞态。

社区通过 Issue → Fork → Branch → PR → 只读 CI → 维护者审核 → Merge → Release。新增平台须提供实际环境、合成日志和完整文档；未测必须标 UNTESTED。维护者账户尚未确认，CODEOWNERS 无有效规则；公开前须配置至少一名独立审核、必须 CI 通过、禁止强制推送、限制直接写主分支及私密漏洞渠道。不能公开提交秘密或真实客户材料。

本阶段未获 commit/push/公开建库/发布授权。公开前审核 PUBLIC_RELEASE_REVIEW.md 和完整哈希清单，确认许可证归属、品牌、维护者及公开文件白名单。正式发布必须建立独立空仓库，不得 fork、继承或改变原私人仓库的可见性。软件和本地工具免费；用户选择的模型可能另收费。
