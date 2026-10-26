# Updates / 社区升级
Semantic Versioning: MAJOR for incompatible contract/schema, MINOR for compatible capabilities, PATCH for fixes. Update VERSION.json, script version, template compatibility and CHANGELOG together. Schema changes require tested reversible migration with explicit approval.

check-updates is OFFLINE by default. `check-updates --online --repo OWNER/REPO` reads latest release metadata, no credentials or downloads. Status distinguishes OFFLINE, NO_AUTH, API_LIMIT and PRIVATE_REPO_OR_NOT_FOUND (hidden private/nonexistent cannot be distinguished without authorization). Digests are shown when available; signature status is NOT_VERIFIED. Missing digest is not trust.

Obtain a candidate manually. `upgrade --candidate DIRECTORY --dry-run` lists script/file changes, hashes, permissions and migration policy. After human code review: `upgrade --candidate DIRECTORY --approve-sha256 CANDIDATE_HASH --install-to NEW_EMPTY_DIRECTORY` copies into a new version directory without executing candidate code or replacing active files. Explicitly select this version in the host; pin its manifest. Partial failed copies stay inactive for inspection. Rollback selects the retained prior directory. Vault rollback is separate.

禁止后台下载执行社区代码。维护者审核和文件哈希不能替代用户批准。安装不迁移私人资料。
