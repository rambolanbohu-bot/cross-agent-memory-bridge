# Import / 跨 AI 导入
A single UTF-8 Markdown snapshot contains schema, local revision, source hash, target, selected records, generated time and content hash. Target labels a recipient; it proves no integration. Manually upload only after recipient review, no GitHub connector required.
Ask the receiving agent for version, content_sha256, source, loaded_files, loaded_at and verified_or_snapshot; repeat three confirmed synthetic facts; distinguish pending; propose but never apply. Without trusted current source hash report UNKNOWN_FRESHNESS. `verify-snapshot --snapshot FILE --path VAULT` compares local state. `--expected-sha256 HASH` accepts a separately trusted source hash (possibly manually verified from remote). This does not automatically read GitHub.
宿主须支持文件读取和技能执行；普通聊天用手工快照。每次刷新须重新导出并批准，旧快照不自动更新。状态见 docs/COMPATIBILITY.md。

An expected hash match alone is SOURCE_HASH_MATCH_UNAUTHENTICATED, not CURRENT: only a full trusted local profile comparison validates selected facts. Generated timestamps are metadata, not signatures.
