"""Run acceptance suite with Python subprocess sockets denied and no API keys."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
ROOT=Path(__file__).resolve().parents[1]
(ROOT/'work').mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(prefix='offline-',dir=ROOT/'work') as folder:
 p=Path(folder)/'sitecustomize.py'
 p.write_text('import sys\ndef deny(event, args):\n if event.startswith("socket."): raise OSError("OFFLINE_TEST_NETWORK_DENIED")\nsys.addaudithook(deny)\n',encoding='utf-8')
 env={k:v for k,v in os.environ.items() if not any(x in k.upper() for x in ('API_KEY','ACCESS_TOKEN','AUTH_TOKEN','OPENAI','ANTHROPIC','GEMINI','GOOGLE_API'))}
 env['PYTHONPATH']=folder;env['PYTHONUTF8']='1';env['PYTHONDONTWRITEBYTECODE']='1'
 sentinel=subprocess.run([sys.executable,'-c','import socket; socket.create_connection(("127.0.0.1",9))'],env=env,capture_output=True,text=True)
 if sentinel.returncode==0 or 'OFFLINE_TEST_NETWORK_DENIED' not in sentinel.stderr:raise SystemExit('Offline guard failed')
 print('OFFLINE guard verified; model keys removed; no external model calls',flush=True)
 p=subprocess.run([sys.executable,'-X','utf8','-B','-m','unittest','discover','-s','tests','-v'],cwd=ROOT,env=env)
 raise SystemExit(p.returncode)
