import ast,json,hashlib,copy
from pathlib import Path
R=Path(__file__).resolve().parent
p=R/'verify.py';s=p.read_text()
old="'split-acceptance.yml', 'closure-maintenance.yml']"
new="'split-acceptance.yml', 'closure-maintenance.yml', 'split-write-acceptance.yml', 'split-write-selftest.yml']"
if new not in s:
 assert s.count(old)==1
 s=s.replace(old,new,1);p.write_text(s)
ns={}
for n in ast.parse(s).body:
 if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in {'CONSUMER_FILES','expected_repo_count','expected_workflow_count'} for t in n.targets):exec(compile(ast.Module(body=[n],type_ignores=[]),'<registry>','exec'),ns)
 if isinstance(n,ast.FunctionDef) and n.name=='render_consumers':exec(compile(ast.Module(body=[n],type_ignores=[]),'<renderer>','exec'),ns)
assert ns['expected_workflow_count']==20 and ns['expected_repo_count']==7
(R/'docs/SHARED-WRITEBACK-CONSUMERS.md').write_text(ns['render_consumers']())
p=R/'manifest.json';m=json.loads(p.read_text());before=copy.deepcopy(m)
for rel in ['verify.py','docs/SHARED-WRITEBACK-CONSUMERS.md','.github/workflows/maintenance.yml','sync_split_consumers.py']:
 b=(R/rel).read_bytes();m['docs_integrity'][rel]=hashlib.sha1(b'blob %d\0'%len(b)+b).hexdigest()
assert m['true_copies']==before['true_copies'] and m['_tested_limits']==before['_tested_limits']
p.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
print('7 repositories / 20 shared-report callers; Agent clocks, history and vendor bytes unchanged')
