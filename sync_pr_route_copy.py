import json,hashlib,urllib.request
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parent
UP='5ed2a58998025b0ff5d9625050945ac858ab3bda';BLOB='da3e4efd6bebfc3763a8eaefe05d88ec5a452131'
def blob(b):return hashlib.sha1(b'blob %d\0'%len(b)+b).hexdigest()
p=R/'manifest.json';m=json.loads(p.read_text());old_limits=list(m['_tested_limits']);old_agents={k:v for k,v in m['true_copies']['copies'].items() if k.startswith('agents/')}
copy=m['true_copies']['copies']['vendor/ci-workflows/report.yml']
if copy.get('source_commit')!=UP:
 with urllib.request.urlopen('https://raw.githubusercontent.com/supercubegame/ci-workflows/'+UP+'/.github/workflows/report.yml',timeout=30) as response:b=response.read()
 assert blob(b)==BLOB and len(b)==22790
 (R/'vendor/ci-workflows/report.yml').write_bytes(b)
 copy.update(source_commit=UP,size_baseline_bytes=len(b),readback_at=datetime.now(timezone.utc).isoformat().replace('+00:00','Z'))
for rel in ['vendor/ci-workflows/report.yml','.github/workflows/maintenance.yml','sync_pr_route_copy.py']:
 m['docs_integrity'][rel]=blob((R/rel).read_bytes())
assert m['_tested_limits']==old_limits
assert {k:v for k,v in m['true_copies']['copies'].items() if k.startswith('agents/')}==old_agents
p.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
print('COPY OK',BLOB,UP,'Agent readbacks unchanged')
