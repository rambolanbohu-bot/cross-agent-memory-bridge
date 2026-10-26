"""Two independent reader processes, labelled SIMULATED, never real third-party agents."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / 'skills/cross-agent-memory-bridge/scripts/memory_bridge.py'

def call(*args):
    p = subprocess.run([sys.executable, '-X', 'utf8', '-B', str(CLI), *map(str, args)], capture_output=True, text=True, encoding='utf-8')
    if p.returncode:
        raise RuntimeError(p.stdout + p.stderr)
    return json.loads(p.stdout)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def reader(role, vault):
    r = call('read', '--path', vault)
    return {'role': role, 'mode': 'SIMULATED_READER_PROCESS', 'facts': [x['text'] for x in r['records']], 'pending_count': r['pending_count'], 'receipt': {k: r[k] for k in ('version', 'content_sha256', 'source', 'loaded_files', 'loaded_at', 'verified_or_snapshot')}}

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--role')
    p.add_argument('--vault')
    a = p.parse_args()
    if a.role:
        print(json.dumps(reader(a.role, a.vault), ensure_ascii=False))
        return
    (ROOT / 'work').mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='simulation-', dir=ROOT / 'work') as t:
        t = Path(t)
        vault = t / 'vault'
        call('init', '--output', vault)
        proposal = t / 'p1.json'
        call('propose', '--path', vault, '--change', ROOT / 'examples/fictional-change.json', '--out', proposal)

        def accept(p, n):
            d = call('diff', '--path', vault, '--proposal', p)
            a = t / (n + '.json')
            call('review', '--path', vault, '--proposal', p, '--reviewer', 'Synthetic human fixture', '--approve-sha256', d['proposal_sha256'], '--out', a)
            return call('apply', '--path', vault, '--proposal', p, '--approval', a)
        accept(proposal, 'a1')
        base = sha(vault / 'profile.json')
        roles = []
        for role in ['Agent-A', 'Agent-B']:
            proc = subprocess.run([sys.executable, '-X', 'utf8', '-B', __file__, '--role', role, '--vault', str(vault)], check=True, capture_output=True, text=True, encoding='utf-8')
            roles.append(json.loads(proc.stdout))
        assert roles[0]['facts'] == roles[1]['facts'] and len(roles[0]['facts']) == 3
        assert all((x['pending_count'] == 1 for x in roles))
        snapshot = t / 'context.md'
        preview = call('export', '--path', vault, '--out', snapshot, '--preview')
        call('export', '--path', vault, '--out', snapshot, '--approve-sha256', preview['export_sha256'])
        old = call('verify-snapshot', '--snapshot', snapshot, '--path', vault)
        assert old['status'] == 'CURRENT'
        change = json.loads((ROOT / 'examples/fictional-change.json').read_text(encoding='utf-8'))
        change['operations'] = change['operations'][:1]
        change['operations'][0]['record'].update(text='Fictional Mira builds paper telescopes.', version=2)
        c = t / 'change.json'
        c.write_text(json.dumps(change), encoding='utf-8')
        p = t / 'p2.json'
        call('propose', '--path', vault, '--change', c, '--out', p)
        assert sha(vault / 'profile.json') == base
        denied = subprocess.run([sys.executable, str(CLI), 'apply', '--path', str(vault), '--proposal', str(p)], capture_output=True)
        assert denied.returncode != 0 and sha(vault / 'profile.json') == base
        updated = accept(p, 'a2')
        assert updated['version'] > old['version']
        stale = call('verify-snapshot', '--snapshot', snapshot, '--path', vault)
        assert stale['status'] == 'STALE'
        remote = call('verify-snapshot', '--snapshot', snapshot, '--expected-sha256', '0' * 64)
        assert remote['status'] == 'STALE'
        result = {'status': 'CROSS_AGENT_SIMULATED_ONLY', 'reader_processes': roles, 'three_facts_agree': True, 'pending_not_confirmed': True, 'unapproved_hash_unchanged': True, 'old_version': old['version'], 'approved_version': updated['version'], 'old_snapshot': stale['status'], 'synthetic_remote_hash_mismatch': remote['status'], 'remote_network_read': False, 'real_third_party_agents_tested': False}
        print(json.dumps(result, ensure_ascii=False, indent=2))
if __name__ == '__main__':
    main()
