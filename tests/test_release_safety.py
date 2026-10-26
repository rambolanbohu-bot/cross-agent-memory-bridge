"""Targeted release gates; synthetic files only, no network/model calls."""
import importlib.util,json,stat,tempfile,unittest,zipfile
from unittest.mock import patch
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('release_check',ROOT/'tools/release_check.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
class ReleaseSafety(unittest.TestCase):
 def setUp(self):
  (ROOT/'work').mkdir(exist_ok=True);t=tempfile.TemporaryDirectory(dir=ROOT/'work');self.addCleanup(t.cleanup);self.p=Path(t.name)
 def archive(self):
  p=self.p/'good.zip';r.make_archive(p,'cross-agent-memory-bridge',dict({'sample.txt':b'synthetic'},**{n:(ROOT/n).read_bytes() for n in ('LICENSE','VERSION.json','README.md','LICENSE_STATUS.md')}),'install-candidate');return p
 def bad(self,names,link=False):
  p=self.p/'bad.zip'
  with zipfile.ZipFile(p,'w') as z:
   for n in names:
    i=zipfile.ZipInfo(n)
    if link:i.external_attr=(stat.S_IFLNK|0o777)<<16
    z.writestr(i,'synthetic')
  return p
 def test_candidate_check(self):self.assertEqual(r.check(ROOT)['status'],'PASS')
 def test_unreviewed_secret_refused(self):
  files=r.collect(ROOT);files['new.txt']=('api_key = '+'SYNTHETIC'*6).encode()
  with self.assertRaises(r.ReleaseError):r.privacy_gate(files,r.bridge(ROOT),json.loads(files['tools/privacy-expected-findings.json']))
 def test_exception_cannot_allow_new_line(self):
  files=r.collect(ROOT);files['skills/cross-agent-memory-bridge/scripts/memory_bridge.py']+=('\npassword = '+'SYNTHETIC'*6).encode()
  with self.assertRaises(r.ReleaseError):r.privacy_gate(files,r.bridge(ROOT),json.loads(files['tools/privacy-expected-findings.json']))
 def test_traversal_absolute_drive_refused(self):
  for n in ['../escape','/absolute','C:/drive','cross-agent-memory-bridge/../escape']:
   with self.subTest(n=n):
    with self.assertRaises(r.ReleaseError):r.checked_members(self.bad([n]))
 def test_archive_symlink_refused(self):
  with self.assertRaises(r.ReleaseError):r.checked_members(self.bad(['cross-agent-memory-bridge/link'],True))
 def test_case_collision_refused(self):
  with self.assertRaises(r.ReleaseError):r.checked_members(self.bad(['cross-agent-memory-bridge/A','cross-agent-memory-bridge/a']))
 def test_windows_reserved_refused(self):
  with self.assertRaises(r.ReleaseError):r.checked_members(self.bad(['cross-agent-memory-bridge/CON.txt']))
 def test_tamper_refused(self):
  files=r.checked_members(self.archive());files['sample.txt']=b'changed';p=self.p/'tampered.zip'
  with zipfile.ZipFile(p,'w') as z:
   for n,d in files.items():z.writestr('cross-agent-memory-bridge/'+n,d)
  with self.assertRaises(r.ReleaseError):r.verify(p)
 def test_extract_no_overwrite(self):
  p=self.archive();dest=self.p/'new';r.extract_new(p,dest)
  with self.assertRaises(r.ReleaseError):r.extract_new(p,dest)
  self.assertEqual((dest/'sample.txt').read_bytes(),b'synthetic')
 def test_wrong_version_refused(self):
  files=r.checked_members(self.archive());m=json.loads(files['PACKAGE_MANIFEST.json']);m['version']='9.0.0';files['PACKAGE_MANIFEST.json']=r.encoded(m);files['PACKAGE_MANIFEST.sha256']=(r.sha(files['PACKAGE_MANIFEST.json'])+'  PACKAGE_MANIFEST.json\n').encode();p=self.p/'wrong.zip'
  with zipfile.ZipFile(p,'w') as z:
   for n,d in files.items():z.writestr('cross-agent-memory-bridge/'+n,d)
  with self.assertRaises(r.ReleaseError):r.verify(p)
 def test_build_no_overwrite(self):
  d=self.p/'dist';d.mkdir();f=d/'cross-agent-memory-bridge-v1.0.0-source-candidate.zip';f.write_bytes(b'sentinel')
  with self.assertRaises(r.ReleaseError):r.build(ROOT,d)
  self.assertEqual(f.read_bytes(),b'sentinel')
 def test_normalized_duplicate_refused(self):
  with self.assertRaises(r.ReleaseError):r.checked_members(self.bad(['cross-agent-memory-bridge/a.txt','cross-agent-memory-bridge/./a.txt']))
 def test_oversize_preflight_before_any_decompression(self):
  p=self.p/'oversize.zip'
  with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED) as z:z.writestr('cross-agent-memory-bridge/big.txt',b'x'*1048577)
  with patch.object(zipfile.ZipFile,'open',side_effect=AssertionError('Decompression before metadata preflight')):
   with self.assertRaises(r.ReleaseError):r.checked_members(p)
 def test_wrong_license_holder_refused(self):
  files=r.collect(ROOT);files['LICENSE']=files['LICENSE'].replace(b'2026 Rambo',b'2026 UNKNOWN')
  with self.assertRaises(r.ReleaseError):r.validate_mit(files)
 def test_changed_standard_terms_refused(self):
  files=r.collect(ROOT);files['LICENSE']+=b'Additional legal restriction.\n'
  with self.assertRaises(r.ReleaseError):r.validate_mit(files)
 def test_version_license_disagreement_refused(self):
  files=r.collect(ROOT);version=json.loads(files['VERSION.json']);version['license']='UNKNOWN';files['VERSION.json']=r.encoded(version)
  with self.assertRaises(r.ReleaseError):r.validate_mit(files)
 def test_pr_cannot_execute_release_build(self):
  files=r.collect(ROOT);files['.github/workflows/ci.yml']+=b'      - run: python tools/release_check.py build --root . --dist dist\n'
  with patch.object(r,'collect',return_value=files):
   with self.assertRaises(r.ReleaseError):r.check(ROOT)
 def test_manual_build_fails_without_enable_guard(self):
  files=r.collect(ROOT);name='.github/workflows/candidate-check.yml';files[name]=files[name].replace(b'RELEASE_CANDIDATE_CHECKS_ENABLED',b'UNGUARDED')
  with patch.object(r,'collect',return_value=files):
   with self.assertRaises(r.ReleaseError):r.check(ROOT)
if __name__=='__main__':unittest.main()
