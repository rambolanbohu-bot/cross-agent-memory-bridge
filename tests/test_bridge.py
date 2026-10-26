import json, subprocess, sys, tempfile, unittest, os, uuid
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / 'skills/cross-agent-memory-bridge/scripts/memory_bridge.py'

class BridgeTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='bridge 中文 space ', dir=ROOT / 'work')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.vault = self.root / '档案 space'

    def cli(self, *a, ok=True):
        p = subprocess.run([sys.executable, '-X', 'utf8', str(CLI), *map(str, a)], capture_output=True, text=True, encoding='utf-8')
        if ok:
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        else:
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
        return json.loads(p.stdout)

    def init(self):
        return self.cli('init', '--output', self.vault)

    def file(self, n, d):
        p = self.root / n
        p.write_text(json.dumps(d, ensure_ascii=False), encoding='utf-8')
        return p

    def change(self, text='Enjoys astronomy'):
        return {'why': 'Synthetic correction', 'source': 'user', 'operations': [{'op': 'upsert', 'record': {'id': 'fact-001', 'text': text, 'source': 'user', 'created_at': '2026-10-26', 'verified_at': '2026-10-26', 'status': 'confirmed', 'tags': ['hobby'], 'visibility': 'shareable', 'sensitive': False, 'version': 1}}]}

    def proposal(self, c=None):
        p = self.root / ('proposal-' + uuid.uuid4().hex + '.json')
        self.cli('propose', '--path', self.vault, '--change', self.file('change.json', c or self.change()), '--out', p)
        return p

    def approval(self, p):
        a = self.root / ('approval-' + uuid.uuid4().hex + '.json')
        d = self.cli('diff', '--path', self.vault, '--proposal', p)
        self.cli('review', '--path', self.vault, '--proposal', p, '--reviewer', 'Synthetic user', '--approve-sha256', d['proposal_sha256'], '--out', a)
        return a

    def apply(self, p, a):
        return self.cli('apply', '--path', self.vault, '--proposal', p, '--approval', a)

    def test_init_validate_no_overwrite(self):
        self.init()
        self.cli('validate', '--path', self.vault)
        self.assertEqual(self.cli('read', '--path', self.vault)['records'], [])
        self.cli('init', '--output', self.vault, ok=False)

    def test_approval_replay_rollback(self):
        v = self.init()
        p = self.proposal()
        before = (self.vault / 'profile.json').read_bytes()
        self.cli('apply', '--path', self.vault, '--proposal', p, ok=False)
        self.assertEqual(before, (self.vault / 'profile.json').read_bytes())
        a = self.approval(p)
        self.apply(p, a)
        self.cli('apply', '--path', self.vault, '--proposal', p, '--approval', a, ok=False)
        s = self.cli('status', '--path', self.vault)
        self.cli('rollback', '--path', self.vault, '--version', v['version'], ok=False)
        self.cli('rollback', '--path', self.vault, '--version', v['version'], '--approve-sha256', s['content_sha256'])
        self.assertEqual(self.cli('read', '--path', self.vault)['records'], [])

    def test_tamper_and_competing_edit(self):
        self.init()
        p = self.proposal()
        a = self.approval(p)
        d = json.loads(p.read_text(encoding='utf-8'))
        d['why'] = 'tampered'
        p.write_text(json.dumps(d), encoding='utf-8')
        self.cli('apply', '--path', self.vault, '--proposal', p, '--approval', a, ok=False)
        p = self.proposal()
        a = self.approval(p)
        f = self.vault / 'profile.json'
        d = json.loads(f.read_text(encoding='utf-8'))
        d['unexpected'] = True
        f.write_text(json.dumps(d), encoding='utf-8')
        self.cli('apply', '--path', self.vault, '--proposal', p, '--approval', a, ok=False)

    def test_export_filter_and_stale(self):
        self.init()
        c = self.change()
        r = c['operations'][0]['record']
        for id, status, vis in [('fact-002', 'pending', 'shareable'), ('fact-003', 'confirmed', 'private')]:
            c['operations'].append({'op': 'upsert', 'record': dict(r, id=id, text=id, status=status, visibility=vis)})
        p = self.proposal(c)
        self.apply(p, self.approval(p))
        out = self.root / '快照.md'
        args = ['export', '--path', self.vault, '--target', 'muse', '--out', out]
        preview = self.cli(*args, '--preview')
        self.assertFalse(out.exists())
        self.cli(*args, ok=False)
        self.cli(*args, '--approve-sha256', preview['export_sha256'])
        t = out.read_text(encoding='utf-8')
        self.assertIn('Enjoys astronomy', t)
        self.assertNotIn('fact-002', t)
        self.assertNotIn('fact-003', t)
        self.assertEqual(self.cli('verify-snapshot', '--snapshot', out, '--path', self.vault)['status'], 'CURRENT')
        c = self.change('Prefers concise summaries')
        c['operations'][0]['record']['version'] = 2
        p = self.proposal(c)
        self.apply(p, self.approval(p))
        self.assertEqual(self.cli('verify-snapshot', '--snapshot', out, '--path', self.vault)['status'], 'STALE')

    def test_secrets_encoding_obfuscation_names(self):
        self.init()
        for n, t, e in [('key.txt', 'api_key = ' + 'abCD12' * 8, 'utf-8'), ('混淆.txt', 'a\u200bpi_key = ' + 'EFgh34' * 8, 'utf-16'), ('客户流水.csv', 'synthetic client', 'utf-8')]:
            (self.vault / n).write_text(t, encoding=e)
        r = self.cli('privacy-check', '--path', self.vault, ok=False)
        self.assertGreaterEqual(len(r['findings']), 3)
        self.assertNotIn('abCD12', json.dumps(r))

    def test_hidden_large_binary_traversal_zip(self):
        self.init()
        (self.vault / '.hidden').mkdir()
        (self.vault / '.hidden' / 'secret').write_text('opaque', encoding='utf-8')
        (self.vault / 'big.txt').write_bytes(b'a' * 1048577)
        (self.vault / 'bin.bin').write_bytes(b'\x00\xff')
        self.cli('privacy-check', '--path', self.vault, ok=False)
        self.cli('validate', '--path', str(self.vault / '..' / '档案 space'), ok=False)
        import zipfile
        z = self.root / 'bad.zip'
        with zipfile.ZipFile(z, 'w') as f:
            f.writestr('../escape.txt', 'no')
        self.cli('inspect-archive', '--archive', z, ok=False)
        self.assertFalse((self.root / 'escape.txt').exists())

    def test_duplicate_and_sensitive_merge(self):
        self.init()
        c = self.change()
        c['operations'] *= 2
        for c in [c, self.change('Bank account 1234567890123456')]:
            self.cli('propose', '--path', self.vault, '--change', self.file('bad.json', c), '--out', self.root / 'bad-proposal.json', ok=False)

    def test_staged_secret(self):
        self.init()

        def git(*a):
            subprocess.run(['git', '-C', str(self.vault), *a], check=True, capture_output=True)
        git('init')
        f = self.vault / 'staged.txt'
        f.write_text('api_key = ' + 'ZyXw98' * 8, encoding='utf-8')
        git('add', 'staged.txt')
        f.write_text('clean', encoding='utf-8')
        r = self.cli('privacy-check', '--path', self.vault, '--staged', ok=False)
        self.assertTrue(any((x['location'].startswith('git-index:') for x in r['findings'])))

    def test_link(self):
        self.init()
        dest = self.root / 'outside'
        dest.mkdir()
        link = self.vault / 'linked'
        if os.name == 'nt':
            p = subprocess.run(['cmd', '/c', 'mklink', '/J', str(link), str(dest)], capture_output=True)
            if p.returncode:
                self.skipTest('Windows junction creation denied by sandbox; real junction UNTESTED')
            self.addCleanup(lambda: os.rmdir(link) if link.exists() else None)
        else:
            link.symlink_to(dest, target_is_directory=True)
        self.cli('privacy-check', '--path', self.vault, ok=False)
        self.cli('read', '--path', link, ok=False)

    def test_offline_update_migrate_skill(self):
        self.init()
        self.cli('skill-validate', '--path', CLI.parents[1])
        self.assertEqual(self.cli('check-updates')['status'], 'OFFLINE')
        self.cli('migrate', '--path', self.vault, '--to-schema', '1.0', '--dry-run')
        self.cli('migrate', '--path', self.vault, '--to-schema', '2.0', ok=False)
        self.cli('upgrade', '--candidate', ROOT, '--dry-run')
if __name__ == '__main__':
    unittest.main()
