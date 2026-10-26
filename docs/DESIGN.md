# Design decisions
The restored master task is the specification. The user explicitly requested direct implementation without another design approval round. Python standard library plus one atomic JSON envelope gives a small auditable offline system. A database adds deployment burden; Git as the fact store complicates consent. Git is optional.

```mermaid
flowchart LR
 Agent --> Proposal
 Vault[Local profile.json] --> Reader[Safe read]
 Proposal --> Diff
 Diff --> Human[Human approval]
 Human --> Apply[Locked hash check and atomic replace]
 Apply --> Vault
 Apply --> Backups[Local versions]
 Vault --> Preview
 Human --> Preview
 Preview --> Snapshot[Manual snapshot]
 Backups --> Rollback[Approved restore as new revision]
 Rollback --> Vault
```
The canonical JSON includes audit metadata. Write history before canonical replacement. A crash may leave an orphan version; later revisions skip occupied numbers. History mismatch blocks writes. Cooperating writers serialize by exclusive lock; hostile same-user writers are outside this portable protocol. Never auto-delete stale locks.
Tree changes: behavior tests are grouped by feature in test_bridge.py/test_security.py; no dependabot without dependencies. CODEOWNERS is deliberately unassigned pending confirmed maintainer. Source skill stays under skills/. Optional project-local discovery copies are only for validation.
