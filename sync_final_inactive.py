import ast,copy,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent
p=R/'docs/QUINN-FIELD-NOTES.md';s=p.read_text()
head='## meetnote：两种相反的失效'
policy='''### 当前适用策略（2026-09-07，优先于下方历史规则）

用户明确不使用 meetnote，已合并 [meetnote #9](https://github.com/supercubegame/meetnote/pull/9)。push、PR、schedule 只跑快测试与报告；真实 StepFun 请求仅在 workflow_dispatch 且 run_live=true 时运行，默认 false。

巡检先核对 meetnote 的 README 与 .github/workflows/verify.yml，确认手动开关仍生效，再看快测试和回写；不能将 live skipped 算成接口恢复。停用期间旧 .github/live-heartbeat.json 是历史证据，超过 48 小时不按意外停机报警，不要求恢复订阅，也不要求重新启用自动真实请求。

历史 issue #4 保留，不自动关闭；未取得新有效响应，不宣称恢复。基线可继续记录旧心跳，但必须标注“主动停用，历史时间戳”，不累计成新的故障天数。

本次只更新仓内权威档案，没有修改 live Agent。需要在下一次巡检报告中确认观察者确实读到了本节；不能把档案更新等同于已观察到 Agent 行为改变。

### 以下是自动 live 监测启用时期的历史判据

下方记录保留用于理解旧事故，不适用于当前停用状态；只有用户明确恢复自动监测并重新审查触发、心跳与告警策略后才重新采用。

'''
if '### 当前适用策略（2026-09-07' not in s:
 assert s.count(head)==1;s=s.replace(head,head+'\n\n'+policy,1);p.write_text(s)
p=R/'verify.py';v=p.read_text()
helper='''def inactive_policy_problems(text):
    start = text.find('## meetnote：两种相反的失效')
    end = text.find('## flappycat：', start)
    if start < 0 or end < 0:
        return ['meetnote policy section missing']
    region = text[start:end]
    tokens = ['当前适用策略（2026-09-07', 'run_live=true', '默认 false',
              '超过 48 小时不按意外停机报警', '不要求恢复订阅', '不自动关闭',
              '没有修改 live Agent', '历史判据']
    return ['inactive monitoring policy missing: '+t for t in tokens if t not in region]


'''
if 'def inactive_policy_problems(' not in v:
 anchor='def verifier_helpers_selftest():';assert v.count(anchor)==1;v=v.replace(anchor,helper+anchor,1)
 a=v.index(anchor);z=v.index('    return bad',a)
 more="""    policy_text = (ROOT/'docs/QUINN-FIELD-NOTES.md').read_text(encoding='utf-8')
    bad.extend(inactive_policy_problems(policy_text))
    for token in ['run_live=true', '不要求恢复订阅', '超过 48 小时不按意外停机报警']:
        mutant = policy_text.replace(token, '')
        if mutant == policy_text or not inactive_policy_problems(mutant):
            bad.append('inactive-policy deletion control failed: '+token)
    if not inactive_policy_problems(''):
        bad.append('empty policy accepted')
"""
 v=v[:z]+more+v[z:];p.write_text(v)
ns={'ROOT':R}
for node in ast.parse(v).body:
 if isinstance(node,ast.FunctionDef) and node.name=='inactive_policy_problems':exec(compile(ast.Module(body=[node],type_ignores=[]),'<actual-policy-check>','exec'),ns)
assert not ns['inactive_policy_problems'](s)
for token in ['run_live=true','不要求恢复订阅','超过 48 小时不按意外停机报警']:
 assert ns['inactive_policy_problems'](s.replace(token,''))
assert ns['inactive_policy_problems']('')
mfile=R/'manifest.json';m=json.loads(mfile.read_text());before=copy.deepcopy(m)
for rel in ['docs/QUINN-FIELD-NOTES.md','verify.py','.github/workflows/maintenance.yml','sync_final_inactive.py']:
 b=(R/rel).read_bytes();m['docs_integrity'][rel]=hashlib.sha1(b'blob %d\0'%len(b)+b).hexdigest()
assert m['true_copies']==before['true_copies'] and m['_tested_limits']==before['_tested_limits']
mfile.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
print('Inactive policy 5/5: actual section accepted; three missing-token mutants and empty section rejected; live Agent/readback timestamps unchanged.')
