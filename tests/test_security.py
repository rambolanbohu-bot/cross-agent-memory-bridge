"""Negative invariants using synthetic data only."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch
import test_bridge as tb
ROOT, CLI = (tb.ROOT, tb.CLI)
spec = importlib.util.spec_from_file_location('bridge', CLI)
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)

class SecurityTests(unittest.TestCase):
    setUp = tb.BridgeTests.setUp
    cli = tb.BridgeTests.cli
    init = tb.BridgeTests.init
    file = tb.BridgeTests.file
    change = tb.BridgeTests.change
    proposal = tb.BridgeTests.proposal
    approval = tb.BridgeTests.approval
    apply = tb.BridgeTests.apply

    def test_expired_proposal(self):
        self.init()
        p = self.proposal()
        d = json.loads(p.read_text(encoding='utf-8'))
        d['expires_at'] = '2000-01-01T00:00:00+00:00'
        d['proposal_sha256'] = b.digest({k: v for k, v in d.items() if k != 'proposal_sha256'})
        p.write_text(json.dumps(d), encoding='utf-8')
        self.cli('diff', '--path', self.vault, '--proposal', p, ok=False)

    def test_combined_sensitive_records(self):
        self.init()
        c = self.change()
        c['operations'][0]['record']['text'] = 'bank account 1234567890123456'
        self.cli('propose', '--path', self.vault, '--change', self.file('combined.json', c), '--out', self.root / 'proposal.json', ok=False)

    def test_revoke_and_conflict(self):
        self.init()
        p = self.proposal()
        old = p
        self.apply(p, self.approval(p))
        self.cli('diff', '--path', self.vault, '--proposal', old, ok=False)
        p = self.proposal({'why': 'Synthetic revoke', 'source': 'user', 'operations': [{'op': 'revoke', 'id': 'fact-001'}]})
        self.apply(p, self.approval(p))
        self.assertEqual(self.cli('read', '--path', self.vault)['records'], [])

    def test_lock_and_failed_replace_preserve_canonical(self):
        self.init()
        p = self.proposal()
        a = self.approval(p)
        before = (self.vault / 'profile.json').read_bytes()
        (self.vault / '.bridge-lock').write_text('synthetic held lock', encoding='utf-8')
        self.cli('apply', '--path', self.vault, '--proposal', p, '--approval', a, ok=False)
        (self.vault / '.bridge-lock').unlink()
        real = b.os.replace

        def crash(src, dest):
            if Path(dest).name == 'profile.json':
                raise OSError('Synthetic replace failure')
            return real(src, dest)
        with patch.object(b.os, 'replace', side_effect=crash):
            with self.assertRaises(OSError):
                b.apply(self.vault, p, a)
        self.assertEqual(before, (self.vault / 'profile.json').read_bytes())
        self.assertFalse((self.vault / '.bridge-lock').exists())
        self.apply(p, a)

    def test_approval_bound_to_target_and_stale_export(self):
        self.init()
        p = self.proposal()
        self.apply(p, self.approval(p))
        out = self.root / 'snap.md'
        token = self.cli('export', '--path', self.vault, '--out', out, '--target', 'generic', '--preview')['export_sha256']
        self.cli('export', '--path', self.vault, '--out', out, '--target', 'codex', '--approve-sha256', token, ok=False)
        c = self.change('Prefers diagrams')
        c['operations'][0]['record']['version'] = 2
        p = self.proposal(c)
        self.apply(p, self.approval(p))
        self.cli('export', '--path', self.vault, '--out', out, '--approve-sha256', token, ok=False)

    def test_missing_approval_and_modified_approval(self):
        self.init()
        p = self.proposal()
        a = self.approval(p)
        d = json.loads(a.read_text(encoding='utf-8'))
        d['base_version'] = 999
        a.write_text(json.dumps(d), encoding='utf-8')
        self.cli('apply', '--path', self.vault, '--proposal', p, '--approval', a, ok=False)

    def test_snapshot_integrity(self):
        self.init()
        out = self.root / 'snap.md'
        preview = b.export(self.vault, 'generic', out, True, None)
        b.export(self.vault, 'generic', out, False, preview['export_sha256'])
        self.assertEqual(b.verify_snapshot(out)['status'], 'UNKNOWN_FRESHNESS')
        out.write_text(out.read_text(encoding='utf-8').replace('"version": 1', '"version": 2'), encoding='utf-8')
        with self.assertRaises(b.BridgeError):
            b.verify_snapshot(out)

    def test_link_detection_with_synthetic_reparse_attributes(self):
        fake = type('SyntheticStat', (), {'st_mode': 0, 'st_file_attributes': 1024})()
        with patch.object(Path, 'lstat', return_value=fake):
            self.assertTrue(b.linklike(Path('synthetic')))

    def test_socket_denied_core(self):
        with patch('socket.socket', side_effect=AssertionError('Network forbidden')):
            b.init(self.vault)
            b.profile(self.vault)
            b.privacy(self.vault)
            self.assertEqual(b.check_updates()['status'], 'OFFLINE')

    def test_upgrade_explicit_copy_no_execution(self):
        plan = b.upgrade(ROOT, True)
        dest = self.root / 'installed'
        with self.assertRaises(b.BridgeError):
            b.upgrade(ROOT, False, None, dest)
        r = b.upgrade(ROOT, False, plan['candidate_sha256'], dest)
        self.assertEqual(r['status'], 'COPIED_NOT_EXECUTED')
        self.assertEqual(b.package_manifest(dest), plan['candidate_manifest'])
        with self.assertRaises(b.BridgeError):
            b.upgrade(ROOT, False, plan['candidate_sha256'], dest)

    def test_template_scan_clean(self):
        self.assertEqual(b.privacy(CLI.parents[1] / 'assets/templates')['findings'], [])

    def test_duplicate_json_key_rejected(self):
        f = self.root / 'duplicate.json'
        f.write_text('{"x":1,"x":2}', encoding='utf-8')
        with self.assertRaises(b.BridgeError):
            b.load(f)

    def test_default_private_and_pending_not_loaded(self):
        self.init()
        c = self.change()
        r = c['operations'][0]['record']
        r['status'] = 'pending'
        r['verified_at'] = None
        r['visibility'] = 'private'
        p = self.proposal(c)
        self.apply(p, self.approval(p))
        d = self.cli('read', '--path', self.vault)
        self.assertEqual(d['records'], [])
        self.assertEqual(d['pending_count'], 1)

    def test_snapshot_rehashed_lie_not_current(self):
        self.init()
        out = self.root / 'snap.md'
        plan = b.export(self.vault, 'generic', out, True, None)
        b.export(self.vault, 'generic', out, False, plan['export_sha256'])
        t = out.read_text(encoding='utf-8')
        start = t.index('```json\n') + 8
        end = t.index('```', start)
        d = json.loads(t[start:end])
        d['records'] = [self.change()['operations'][0]['record']]
        d['content_sha256'] = b.digest({k: d[k] for k in ('schema_version', 'version', 'source', 'source_sha256', 'target', 'records')})
        out.write_text(t[:start] + b.encoded(d).decode() + t[end:], encoding='utf-8')
        self.assertNotEqual(b.verify_snapshot(out, self.vault)['status'], 'CURRENT')

    def test_fact_with_markdown_fence_roundtrip(self):
        self.init()
        p = self.proposal(self.change('Prefers literal ``` in examples'))
        self.apply(p, self.approval(p))
        out = self.root / 'snap.md'
        plan = b.export(self.vault, 'generic', out, True, None)
        b.export(self.vault, 'generic', out, False, plan['export_sha256'])
        self.assertEqual(b.verify_snapshot(out, self.vault)['status'], 'CURRENT')

    def test_null_record_json_error(self):
        self.init()
        c = self.change()
        c['operations'][0]['record'] = None
        self.cli('propose', '--path', self.vault, '--change', self.file('null.json', c), '--out', self.root / 'p.json', ok=False)

    def test_merged_size_limit_preserves_profile(self):
        self.init()
        base = b.profile(self.vault)
        result = copy.deepcopy(base)
        for i in range(300):
            r = copy.deepcopy(self.change()['operations'][0]['record'])
            r['id'] = f'large-{i}'
            r['text'] = str(i) + 'x' * 3900
            result['records'].append(r)
        before = (self.vault / 'profile.json').read_bytes()
        with self.assertRaises(b.BridgeError):
            b.commit_state(self.vault, base, result, 'apply', 'synthetic', 'size regression', 'synthetic')
        self.assertEqual(before, (self.vault / 'profile.json').read_bytes())
if __name__ == '__main__':
    unittest.main()
