"""Local release packaging/privacy gates; no network, credentials, install or publish."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import zipfile
VERSION='1.0.0'
MIT_BODY_SHA256='fe2a9817987f862eaced948f0468c7f51d2fedfc48c5c505b246a49a3870e9a5'
EXCLUDED={'work','dist','__pycache__','.git'}
SPECIAL={'PACKAGE_MANIFEST.json','PACKAGE_MANIFEST.sha256'}
class ReleaseError(Exception):pass
def require(test,message):
    if not test:raise ReleaseError(message)
def sha(data):return hashlib.sha256(data).hexdigest()
def encoded(obj):return (json.dumps(obj,sort_keys=True,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
def linked(p):
    s=p.lstat();return stat.S_ISLNK(s.st_mode) or bool(getattr(s,'st_file_attributes',0)&0x400)
def collect(root):
    root=Path(root).absolute();require(not linked(root),'Reparse/link root forbidden');out={}
    def visit(folder):
        for p in sorted(folder.iterdir()):
            rel=p.relative_to(root)
            if any(x in EXCLUDED for x in rel.parts):continue
            require(not linked(p),'Link/reparse forbidden: '+rel.as_posix())
            if p.is_dir():visit(p)
            else:
                require(p.is_file() and p.stat().st_size<=1048576,'Nonregular/oversized file')
                require(len(out)<2000,'File budget exceeded')
                out[rel.as_posix()]=p.read_bytes()
    visit(root);return out

def bridge(root):
    path=Path(root)/'skills/cross-agent-memory-bridge/scripts/memory_bridge.py'
    spec=importlib.util.spec_from_file_location('release_bridge',path);b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b);return b

def privacy_gate(files,b,exceptions):
    hard=[];all_findings=[];accepted=[]
    rules=[('ABSOLUTE_USER_PATH',r'(?:[A-Za-z]:[\\/]+Users[\\/]+|/(?:Users|home)/)[^\s\x22\x27<>]+'),('FAILED_TRACEBACK',r'Traceback \(most recent call last\)')]
    allowed={(x['path'],x['category'],x['line_sha256']):x['reason'] for x in exceptions}
    for name,data in files.items():
        parts=PurePosixPath(name).parts
        if any(x in {'.agents','.codex','.aws','.env','auth.json','credentials.json'} for x in parts) or name.endswith(('.pyc','.tmp','.bak','.local.json','.local.md')):hard.append({'category':'FORBIDDEN_MEMBER','location':name})
        findings=b.scan_data(data,name)
        try:lines=data.decode('utf-8-sig').splitlines()
        except UnicodeError:lines=[]
        for category,pattern in rules:
            for line,text in enumerate(lines,1):
                if re.search(pattern,text,re.I):findings.append({'category':category,'location':name,'line':line})
        for f in findings:
            all_findings.append(f)
            line=f.get('line');fingerprint=sha(lines[line-1].encode('utf-8')) if isinstance(line,int) and 0<line<=len(lines) else None
            key=(name,f['category'],fingerprint)
            if key in allowed:accepted.append(dict(f,line_sha256=fingerprint,reason=allowed[key]))
            else:hard.append(f)
    require(not hard,'Unreviewed privacy findings: '+json.dumps(hard,ensure_ascii=True))
    return {'status':'PASS_WITH_REVIEWED_SYNTHETIC_FINDINGS' if accepted else 'PASS','findings':all_findings,'reviewed_exceptions':accepted,'unreviewed_count':0,'manual_review_still_required':True}

def validate_mit(files):
    require({'LICENSE','VERSION.json','README.md','LICENSE_STATUS.md'}<=files.keys(),'Missing MIT package materials')
    text=files['LICENSE'].decode('utf-8-sig')
    require(text.splitlines()[2]=='Copyright (c) 2026 Rambo','Wrong or unresolved copyright holder')
    require('Permission is hereby granted' in text,'Missing complete MIT terms')
    body='Permission is hereby granted'+text.split('Permission is hereby granted',1)[1]
    require(sha(' '.join(body.split()).encode())==MIT_BODY_SHA256,'Standard MIT terms were changed')
    version=json.loads(files['VERSION.json'])
    require(version.get('version')==VERSION and version.get('license')=='MIT' and version.get('license_status')=='MIT_CONFIRMED','MIT/version status mismatch')
    require(version.get('copyright_holder')=='Rambo' and version.get('copyright_year')==2026,'Version attribution mismatch')
    for name in ('README.md','README.zh-CN.md'):
        if name in files:
            readme=files[name].decode('utf-8-sig')
            require(all(term in readme for term in ('MIT','Rambo',VERSION)),'README license/version mismatch')
            require('COPYRIGHT HOLDER TO BE CONFIRMED' not in readme and 'NOT selected a public license' not in readme,'Obsolete license pending claim')
    prefix='skills/cross-agent-memory-bridge/'
    if prefix+'SKILL.md' in files:
        require(files[prefix+'LICENSE']==files['LICENSE'],'Root and Skill LICENSE mismatch')
        require(files[prefix+'VERSION.json']==files['VERSION.json'],'Root and Skill version mismatch')
        require('license: MIT' in files[prefix+'SKILL.md'].decode(),'Skill license metadata missing')
    require('LICENSE_DECISION_REQUIRED.md' not in files,'Obsolete license decision file')
    return {'license':'MIT','holder':'Rambo','year':2026,'public_actions_authorized':False}

def check(root):
    root=Path(root).absolute();files=collect(root);b=bridge(root)
    required={'README.md','README.zh-CN.md','INSTALLATION.md','COMPATIBILITY.md','PRIVACY.md','SECURITY.md','CONTRIBUTING.md','CHANGELOG.md','RELEASE_CHECKLIST.md','.github/workflows/ci.yml'}
    require(required<=files.keys(),'Required documents or CI missing')
    ci=files['.github/workflows/ci.yml'].decode('utf-8-sig')
    require('contents: read' in ci and 'persist-credentials: false' in ci,'CI permissions not restricted')
    require(not any(x in ci for x in ('pull_request_target','secrets.', 'contents: write','gh release','git push','pypi')), 'Unsafe CI action')
    actions=re.findall(r'uses: (\S+)',ci)
    require(len(actions)==2 and all(re.fullmatch(r'actions/(?:checkout|setup-python)@[a-f0-9]{40}',x) for x in actions),'CI actions not minimal/pinned')
    require('release_check.py build' not in ci and 'release_check.py verify' not in ci,'PR workflow cannot invoke release candidate build scripts')
    require('.github/workflows/candidate-check.yml' in files,'Manual candidate workflow missing')
    manual=files['.github/workflows/candidate-check.yml'].decode('utf-8-sig')
    require('workflow_dispatch:' in manual and 'pull_request' not in manual and '\n  push:' not in manual,'Candidate workflow must be manual-only')
    require("github.ref == 'refs/heads/main' && vars.RELEASE_CANDIDATE_CHECKS_ENABLED == 'true'" in manual and 'environment: candidate-review' in manual and 'ref: refs/heads/main' in manual,'Candidate workflow is not fail-closed on protected main')
    require('contents: read' in manual and 'persist-credentials: false' in manual and not any(x in manual for x in ('secrets.', 'contents: write','gh release','git push','upload-artifact')), 'Candidate workflow must not upload or publish')
    require(all(re.fullmatch(r'actions/(?:checkout|setup-python)@[a-f0-9]{40}',x) for x in re.findall(r'uses: (\S+)',manual)),'Manual workflow actions not pinned')
    require(json.loads(files['VERSION.json'])['version']==VERSION,'Wrong source version')
    validate_mit(files)
    b.skill_validate(root/'skills/cross-agent-memory-bridge')
    exceptions=json.loads(files['tools/privacy-expected-findings.json'])
    report=privacy_gate(files,b,exceptions)
    return {'status':'PASS','files_checked':len(files),'privacy':report,'official_skills_ref':'NOT_RUN','license':'MIT','copyright_holder':'Rambo','license_status':'MIT_CONFIRMED','remote_ci':'NOT_RUN'}

def source_commit(root):
    try:
        import subprocess
        sha_value=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()
        status=subprocess.check_output(['git','-C',str(root),'status','--porcelain'],text=True)
    except (OSError,subprocess.CalledProcessError) as e: raise ReleaseError('Git source proof unavailable') from e
    require(re.fullmatch(r'[0-9a-f]{40}',sha_value) is not None,'Source commit is not a full SHA')
    require(not status,'Source checkout has uncommitted changes')
    return sha_value

def make_archive(destination,prefix,payload,kind,mode='candidate',commit=None):
    entries=[{'path':n,'bytes':len(d),'sha256':sha(d)} for n,d in sorted(payload.items())]
    manifest_data={'version':VERSION,'kind':kind,'license_status':'MIT_CONFIRMED','license':'MIT','copyright_holder':'Rambo','copyright_year':2026,'files':entries,'self_exclusions':sorted(SPECIAL)}
    if mode=='candidate': manifest_data['publication_authorized']=False
    else: manifest_data.update({'manifest_schema':'release-1','source_commit':commit})
    manifest=encoded(manifest_data)
    content=dict(payload);content['PACKAGE_MANIFEST.json']=manifest;content['PACKAGE_MANIFEST.sha256']=(sha(manifest)+'  PACKAGE_MANIFEST.json\n').encode()
    with zipfile.ZipFile(destination,'w',zipfile.ZIP_DEFLATED) as z:
        for name,data in sorted(content.items()):
            info=zipfile.ZipInfo(prefix+'/'+name,date_time=(2026,10,26,0,0,0));info.create_system=3;info.external_attr=(stat.S_IFREG|0o644)<<16;info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,data)
    return {'file':Path(destination).name,'sha256':sha(Path(destination).read_bytes()),'members':len(content)}

def build(root,dist,mode='candidate'):
    root=Path(root).absolute();dist=Path(dist).absolute();check(root)
    commit=source_commit(root) if mode=='release' else None
    require(not dist.exists() or dist.is_dir(),'Dist not directory')
    dist.mkdir(parents=True,exist_ok=True)
    source=collect(root);source={n:d for n,d in source.items() if n not in SPECIAL}
    names=([ 'cross-agent-memory-bridge-v1.0.0-source.zip','cross-agent-memory-bridge-v1.0.0-install.zip'] if mode=='release' else ['cross-agent-memory-bridge-v1.0.0-source-candidate.zip','cross-agent-memory-bridge-v1.0.0-install-candidate.zip'])
    require(not any((dist/n).exists() for n in [*names,'SHA256SUMS.txt']),'Never overwrite an existing candidate distribution')
    skillprefix='skills/cross-agent-memory-bridge/';skill={n[len(skillprefix):]:d for n,d in source.items() if n.startswith(skillprefix)}
    kinds=('source','install') if mode=='release' else ('source-candidate','install-candidate')
    outputs=[make_archive(dist/names[0],'cross-agent-memory-bridge',source,kinds[0],mode,commit),make_archive(dist/names[1],'cross-agent-memory-bridge',skill,kinds[1],mode,commit)]
    (dist/'SHA256SUMS.txt').write_text(''.join(x['sha256']+'  '+x['file']+'\n' for x in outputs),encoding='utf-8')
    for x in outputs:verify(dist/x['file'],mode)
    return {'status':'PASS','archives':outputs,'automatic_publish':False}

def checked_members(archive):
    with zipfile.ZipFile(archive) as z:
        infos=z.infolist();require(len(infos)<=2000,'Archive file budget exceeded')
        planned=[];seen=set();total=0
        # Inspect ALL metadata before decompressing even the first member.
        for i in infos:
            name=i.filename;p=PurePosixPath(name.replace('\\','/'));total+=i.file_size
            require('\\' not in name and name==p.as_posix() and not p.is_absolute() and '..' not in p.parts and ':' not in name,'Unsafe/noncanonical archive path')
            require(not i.is_dir() and not stat.S_ISLNK(i.external_attr>>16),'Directories/links forbidden in manifest package')
            require(i.file_size<=1048576 and total<=20*1048576,'Archive size budget exceeded')
            require(len(p.parts)>=2 and p.parts[0]=='cross-agent-memory-bridge','Unexpected archive root')
            require(not any(part.rstrip(' .').split('.')[0].upper() in {'CON','PRN','AUX','NUL',*[f'COM{x}' for x in range(1,10)],*[f'LPT{x}' for x in range(1,10)]} or part.endswith((' ','.')) for part in p.parts),'Unsafe Windows entry')
            rel=PurePosixPath(*p.parts[1:]).as_posix();key=rel.casefold()
            require(key not in seen,'Duplicate/normalized/case-colliding entry');seen.add(key)
            planned.append((rel,i))
        # Each approved bounded member is read once; ZipFile.read checks its CRC.
        return {rel:z.read(i) for rel,i in planned}

def verify(archive,mode='candidate'):
    files=checked_members(archive);require(SPECIAL<=files.keys(),'Missing integrity metadata')
    manifest=files['PACKAGE_MANIFEST.json'];require(files['PACKAGE_MANIFEST.sha256'].decode().split()[0]==sha(manifest),'Manifest hash mismatch')
    m=json.loads(manifest);require(m['version']==VERSION and m['license_status']=='MIT_CONFIRMED' and m.get('license')=='MIT' and m.get('copyright_holder')=='Rambo' and m.get('copyright_year')==2026,'Unexpected package version/status')
    if mode=='candidate': require(m.get('publication_authorized') is False and 'source_commit' not in m,'Unexpected candidate version/status')
    else: require(m.get('manifest_schema')=='release-1' and re.fullmatch(r'[0-9a-f]{40}',m.get('source_commit','')) and 'publication_authorized' not in m,'Unexpected release manifest')
    expected={x['path']:x for x in m['files']};require(len(expected)==len(m['files']),'Duplicate manifest record')
    require(set(files)==set(expected)|SPECIAL,'Unexpected/missing package members')
    for n,item in expected.items():require(len(files[n])==item['bytes'] and sha(files[n])==item['sha256'],'Member integrity failure: '+n)
    validate_mit(files)
    return {'status':'PASS','license':'MIT','copyright_holder':'Rambo','version':m['version'],'kind':m['kind'],'verified_files':len(expected),'sha256':sha(Path(archive).read_bytes())}

def extract_new(archive,destination):
    verify(archive);files=checked_members(archive);dest=Path(destination).absolute();require(not dest.exists(),'Extraction destination already exists')
    require('..' not in dest.parts,'Traversal destination')
    for p in dest.parents:require(not p.exists() or not linked(p),'Reparse extraction ancestor')
    dest.mkdir(parents=True)
    for name,data in files.items():
        target=dest/name;target.parent.mkdir(parents=True,exist_ok=True)
        with target.open('xb') as f:f.write(data)
    return dest

def main():
    p=argparse.ArgumentParser();s=p.add_subparsers(dest='command',required=True)
    c=s.add_parser('check');c.add_argument('--root',default='.')
    c=s.add_parser('build');c.add_argument('--root',default='.');c.add_argument('--dist',required=True);c.add_argument('--mode',choices=['candidate','release'],default='candidate')
    c=s.add_parser('verify');c.add_argument('--archive',required=True);c.add_argument('--mode',choices=['candidate','release'],default='candidate')
    a=p.parse_args()
    try:
        result=check(a.root) if a.command=='check' else build(a.root,a.dist,a.mode) if a.command=='build' else verify(a.archive,a.mode)
        print(json.dumps(result,ensure_ascii=False,indent=2));return 0
    except (ReleaseError,OSError,ValueError,KeyError,zipfile.BadZipFile) as e:
        print(json.dumps({'status':'FAIL','message':str(e)},ensure_ascii=False));return 2
if __name__=='__main__':raise SystemExit(main())
