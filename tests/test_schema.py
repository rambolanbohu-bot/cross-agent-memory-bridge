import copy
import json
import importlib.util
import unittest
import urllib.error
from unittest.mock import patch
import test_bridge as tb
spec = importlib.util.spec_from_file_location('schema_bridge', tb.CLI)
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)

class SchemaTests(unittest.TestCase):
    setUp = tb.BridgeTests.setUp
    cli = tb.BridgeTests.cli
    init = tb.BridgeTests.init
    change = tb.BridgeTests.change
    file = tb.BridgeTests.file
    proposal = tb.BridgeTests.proposal
    approval = tb.BridgeTests.approval
    apply = tb.BridgeTests.apply

    def test_invalid_schema_fields_and_dates(self):
        self.init()
        base = b.profile(self.vault)
        for key, value in [('status', 'guessed'), ('verified_at', 'not-date'), ('sensitive', 'false'), ('version', True), ('id', '../../outside')]:
            with self.subTest(key=key):
                d = copy.deepcopy(base)
                r = self.change()['operations'][0]['record']
                r[key] = value
                d['records'] = [r]
                with self.assertRaises((b.BridgeError, ValueError)):
                    b.validate_profile(d)

    def test_receipt_reproducible_content_hash(self):
        self.init()
        a = self.cli('read', '--path', self.vault)
        z = self.cli('read', '--path', self.vault)
        self.assertEqual(a['content_sha256'], z['content_sha256'])
        self.assertEqual(a['version'], z['version'])
        p = b.export(self.vault, 'generic', self.root / 'a.md', True, None)
        q = b.export(self.vault, 'generic', self.root / 'b.md', True, None)
        self.assertEqual(p['export_sha256'], q['export_sha256'])

    def test_network_status_classification_no_live_requests(self):
        for code, status in [(401, 'NO_AUTH'), (403, 'API_LIMIT'), (404, 'PRIVATE_REPO_OR_NOT_FOUND'), (429, 'API_LIMIT')]:
            with patch.object(b.urllib.request, 'urlopen', side_effect=urllib.error.HTTPError('https://example.invalid', code, 'synthetic', {}, None)):
                self.assertEqual(b.check_updates('synthetic/project', True)['status'], status)

    def test_zip_symlink_absolute_and_budget(self):
        import zipfile, stat
        for name in ['/absolute.txt', 'C:/drive.txt', 'safe-link']:
            p = self.root / ('zip-' + str(len(name)) + '.zip')
            with zipfile.ZipFile(p, 'w') as z:
                info = zipfile.ZipInfo(name)
                if name == 'safe-link':
                    info.external_attr = (stat.S_IFLNK | 511) << 16
                z.writestr(info, 'synthetic')
            with self.assertRaises(b.BridgeError):
                b.inspect_archive(p)

    def test_secret_categories_do_not_echo_values(self):
        samples = {'PRIVATE_KEY': '-----BEGIN ' + 'PRIVATE KEY-----', 'JWT': 'eyJ' + 'a' * 15 + '.' + 'b' * 20 + '.' + 'c' * 20, 'TOKEN': 'sk-' + 'XyZa98' * 8, 'BANK_OR_ID': '1234567890123456', 'CREDENTIAL': 'password = ' + 'AaZz98' * 8}
        for kind, text in samples.items():
            findings = b.scan_text(text, 'synthetic.txt')
            self.assertTrue(any((f['category'] == kind for f in findings)), kind)
            self.assertNotIn(text, json.dumps(findings))

    def test_utf8_bom_and_utf16_detection(self):
        for encoding in ['utf-8-sig', 'utf-16']:
            data = ('api_key = ' + 'XyZa98' * 8).encode(encoding)
            self.assertTrue(b.scan_data(data, 'synthetic'))
