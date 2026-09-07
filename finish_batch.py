import ast, hashlib, json
from pathlib import Path
R=Path(__file__).resolve().parent
p=R/'verify.py';s=p.read_text()
# Reusable workflow uses must be job-level, not a line embedded inside a run block.
s=s.replace("r'^\\s*uses:", "r'^ {4}uses:")
helpers='''def verifier_helpers_selftest():
    import tempfile
    bad = []
    for raw in ['2026-09-07', '2026-09-07T00:00:00', None, 3, '2026-02-30T00:00:00Z']:
        try:
            aware_readback(raw)
            bad.append('invalid timestamp accepted')
        except ValueError:
            pass
    if aware_readback('2026-09-07T00:00:00Z').tzinfo is None:
        bad.append('valid aware timestamp lost timezone')
    with tempfile.TemporaryDirectory() as d:
        root=Path(d); (root/'docs/nested').mkdir(parents=True)
        (root/'docs/nested/f.md').write_text('x')
        if registered_files(root,['docs']) != {'docs/nested/f.md'}:
            bad.append('recursive registry missed nested file')
    call='supercubegame/ci-workflows/.github/workflows/report.yml@main'
    if not shared_calls('    uses: '+call): bad.append('real job call missed')
    for text in ['#    uses: '+call, '          uses: '+call, '    run: echo '+call]:
        if shared_calls(text): bad.append('comment/run-block fake call accepted')
    return bad


'''
if 'def verifier_helpers_selftest()' not in s:
    s=s.replace('checks = []\n',helpers+'checks = []\n',1)
    old="git_blob(b'') == EMPTY_BLOB, f'空 blob = {git_blob(b\"\")}'"
    new="git_blob(b'') == EMPTY_BLOB and not verifier_helpers_selftest(), f'空 blob = {git_blob(b\"\")} | helper regressions={verifier_helpers_selftest()}'"
    assert old in s;s=s.replace(old,new,1)
if "'closure-maintenance.yml'" not in s:
    s=s.replace("'patch-tracked-ignored.yml', 'split-acceptance.yml']", "'patch-tracked-ignored.yml', 'split-acceptance.yml', 'closure-maintenance.yml']",1)
p.write_text(s)
scope={}
for node in ast.parse(s).body:
    if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id in {'CONSUMER_FILES','expected_repo_count','expected_workflow_count'} for t in node.targets):exec(compile(ast.Module(body=[node],type_ignores=[]),'<registry>','exec'),scope)
    if isinstance(node,ast.FunctionDef) and node.name=='render_consumers':exec(compile(ast.Module(body=[node],type_ignores=[]),'<renderer>','exec'),scope)
(R/'docs/SHARED-WRITEBACK-CONSUMERS.md').write_text(scope['render_consumers']())
note='''# Ecosystem audit, 2026-09-07

This is an observed snapshot, not proof of every job or a future guarantee. Shared report source: commit 7ff526bfad7d6d7e055875574ccf8f686c6f7e48, file blob ccc30dbf35233ea80b8f0f664e3c608ae028fd42.

- TodoX [test PR #21](https://github.com/supercubegame/TodoX/pull/21): existing verification 103/103, three platform packaging and delivery attestation success. Release/screenshots/mirror paths were read, not executed; no force push or publication authorized.
- jumpwow [#10](https://github.com/supercubegame/jumpwow/pull/10): 32/32, engine/browser/report success.
- image-grabber [#12](https://github.com/supercubegame/image-grabber/pull/12): 43/43, fast/browser/report success.
- crossyroad [#7](https://github.com/supercubegame/crossyroad/pull/7): 134/134, engine/browser/report success; heartbeat skipped as expected for branch push.
- flappycat [#5](https://github.com/supercubegame/flappycat/pull/5): 99/100. Existing overdue replace-illustration-shots-with-real-ci-shots obligation caused failure; browser 25/25 passed and report correctly delivered the failure. Do not waive the obligation to obtain green.
- clickup-brain-backup [#154](https://github.com/supercubegame/clickup-brain-backup/pull/154): shared preflight and byte-copy/Agent snapshot closure. The consumer list includes its maintenance workflow planned in this same closure batch; test-only write-acceptance PR #152 is excluded from main inventory while unmerged.
- anyworkflow #108: 22 existing invariant checks and actual delivery attestation passed before final helper/inventory additions. Inspect final PR checks for the final commit.

Agent names, descriptions, schedules, triggers and full visible prompts were read via get_agent and compared in this batch. Both markdown prompt files remain unchanged. Readback is content-level, not raw rich-text-byte fidelity; no live configuration was changed.

PR #106's broad platform claim is not accepted. The account holder reported deliberate deletion in that incident, which explains that event only. The narrow closure is appended to manifest._tested_limits; the old unmerged proposal must not be merged unchanged.

All regression-only PRs and synthetic split PR #153 remain unmerged, pending separate cleanup approval. GitHub Actions automatic PR creation was actually denied; source shards did reach the remote and a test PR was created through the authorized GitHub connection. Subscription recovery in meetnote remains external and unconfirmed.
'''
(R/'docs/ECOSYSTEM-AUDIT-20260907.md').write_text(note)
m=json.loads((R/'manifest.json').read_text())
for rel in ['verify.py','docs/SHARED-WRITEBACK-CONSUMERS.md','docs/ECOSYSTEM-AUDIT-20260907.md','.github/workflows/maintenance.yml','finish_batch.py']:
    b=(R/rel).read_bytes();m['docs_integrity'][rel]=hashlib.sha1(b'blob %d\0'%len(b)+b).hexdigest()
(R/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
print('Finalized helper checks, observed ecosystem evidence and consumer inventory. No thresholds weakened.')
