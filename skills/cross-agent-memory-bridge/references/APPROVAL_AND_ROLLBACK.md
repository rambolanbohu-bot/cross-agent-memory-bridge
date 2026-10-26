# Approval / 审批与回滚
1. change.json has why, source and operations. upsert carries a complete record; revoke carries id.
2. `propose --path VAULT --change change.json --out proposal.json` creates a 24-hour proposal bound to base hash/version; vault unchanged.
3. `diff --path VAULT --proposal proposal.json` shows IDs/record hashes with values redacted. Open local proposal.json and privately review exact text, source, status, sharing settings and why with the human. Hashes alone do not explain meaning.
4. Only after human approval: `review --path VAULT --proposal proposal.json --reviewer USER --approve-sha256 PROPOSAL_HASH --out approval.json`.
5. `apply --path VAULT --proposal proposal.json --approval approval.json` rechecks base, expiry and content under a lock; backs up before atomic replacement. Replay fails.
6. `history --path VAULT` lists value-free audit metadata. `status` gives current content_sha256. After inspecting version N, `rollback --path VAULT --version N --approve-sha256 CURRENT_HASH` restores records as a NEW revision, retaining audit history.
Approval files are consent artifacts, not cryptographic identity proofs. A malicious agent with unrestricted write access can fabricate approval or overwrite files. Host authorization and OS permissions remain essential. why/reviewer may contain private details; keep all vault/audit files out of public repositories.
人须审核具体内容并批准准确哈希，AI 不得自批。异常可能留下未生效版本或残留锁；确认无进程后手工处理。删除敏感资料时还须独立清理历史备份与外部快照。回滚会保留审计并形成新版本。
