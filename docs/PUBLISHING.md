# Publication procedure — not authorization
1. Owner reviews candidate file allowlist, privacy adjudication, tests, license/rights and SHA256. MIT and attribution Rambo (2026) are confirmed. Confirm maintainer/security channel/name and review the rebuilt hashes; publication authorization is still separate.
2. Only with separate explicit authorization create a new EMPTY public repository. Never fork/export private history or change an existing private repository's visibility.
3. Only after commit authorization initialize independent Git, stage allowlist, inspect staged blobs/privacy and diff. Commit/push require separate authorization. This preparation creates no Git repository or staged files.
4. Configure main protection, confirmed CODEOWNERS, private vulnerability reporting and actual CI; maintainer reviews every merge.
5. Separately approve tag v1.0.0 and bilingual Release Notes; publish reviewed packages/hashes and state signature availability honestly.
6. SkillsMP/other directory submission is optional later. Confirm directory terms and required metadata/license; supply only public repository/release, never a private profile or token. No listing/submission performed here.

Any change invalidates old package hashes. Users pin reviewed version/hash and deliberately select upgrades/rollback; no automatic community code execution. 本流程仅准备，不代表执行许可。
