# Self-test / 自测
Run from repo root:
```text
python -X utf8 -m unittest discover -s tests -v
python tools/offline_test.py
python skills/cross-agent-memory-bridge/scripts/memory_bridge.py skill-validate --path skills/cross-agent-memory-bridge
python tools/simulate_agents.py
```
Offline harness denies sockets through sitecustomize in Python subprocesses and removes model API-key environment variables. This is process-level isolation, not a claim that the host network adapter was disabled. Local Git plumbing never contacts a remote.

## Human approval / 人工审批
Create a new vault outside public source. examples/fictional-change.json is synthetic and does not authorize real-person changes.
```text
python skills/cross-agent-memory-bridge/scripts/memory_bridge.py propose --path VAULT --change examples/fictional-change.json --out proposal.json
python skills/cross-agent-memory-bridge/scripts/memory_bridge.py diff --path VAULT --proposal proposal.json
```
Read the local proposal: review every fact, why, source, status and privacy setting. After explicit human approval of proposal_sha256:
```text
python skills/cross-agent-memory-bridge/scripts/memory_bridge.py review --path VAULT --proposal proposal.json --reviewer USER --approve-sha256 PROPOSAL_HASH --out approval.json
python skills/cross-agent-memory-bridge/scripts/memory_bridge.py apply --path VAULT --proposal proposal.json --approval approval.json
python skills/cross-agent-memory-bridge/scripts/memory_bridge.py export --path VAULT --target generic --out reviewed.md --preview
```
Review allowed records with read. After human approval of export_sha256:
```text
python skills/cross-agent-memory-bridge/scripts/memory_bridge.py export --path VAULT --target generic --out reviewed.md --approve-sha256 EXPORT_HASH
python skills/cross-agent-memory-bridge/scripts/memory_bridge.py verify-snapshot --snapshot reviewed.md --path VAULT
python skills/cross-agent-memory-bridge/scripts/memory_bridge.py status --path VAULT
python skills/cross-agent-memory-bridge/scripts/memory_bridge.py rollback --path VAULT --version 1 --approve-sha256 CURRENT_CONTENT_HASH
```
Corrections increment record version. Revoke: `{ "op": "revoke", "id": "fact-001" }`. Rollback creates a new revision; old snapshots become stale. Unsupported migration is refused. Export is not upload. All fixture approvals are synthetic test consent only. macOS/Linux users run the same commands and report exact environment; pending CI is not a passed OS test.
