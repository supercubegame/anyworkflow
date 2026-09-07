"""One bounded CI-side edit. Does not change any live Agent or any existing workflow definition."""
import ast
import hashlib
import json
import re
import subprocess
import tempfile
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def blob(b):
    return hashlib.sha1(b'blob %d\0' % len(b) + b).hexdigest()

def replace(text, old, new):
    if new in text and old not in text:
        return text
    assert text.count(old) == 1, 'unique patch anchor missing: ' + old[:100]
    return text.replace(old, new, 1)

p = ROOT / 'verify.py'
s = p.read_text()
helper = '''def aware_readback(raw):
    if not isinstance(raw, str):
        raise ValueError('readback timestamp must be a string')
    value = datetime.fromisoformat(raw.replace('Z', '+00:00'))
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError('readback timestamp must include a timezone')
    return value


def registered_files(root, directories):
    found = set()
    for directory in directories:
        for f in sorted((root / directory).rglob('*')):
            if '__pycache__' in f.parts or f.suffix == '.pyc':
                continue
            if f.is_symlink():
                raise ValueError('symlink is not a registered content file: ' + str(f))
            if f.is_file():
                found.add(f.relative_to(root).as_posix())
    return found


def shared_calls(text):
    # Only YAML mapping uses values, never comments or a quoted historical mention.
    return re.findall(r'^\\s*uses:\\s*[\\\"\\\']?(supercubegame/ci-workflows/\\.github/workflows/report\\.yml@[^\\s\\\"\\\']+)[\\\"\\\']?\\s*(?:#.*)?$', text, re.M)


'''
s = replace(s, 'checks = []\n', helper + 'checks = []\n')
s = replace(s, "when = datetime.fromisoformat(raw.replace('Z', '+00:00'))", 'when = aware_readback(raw)')
old = "on_disk = set()\nfor d in REGISTERED_DIRS:\n    for f in sorted((ROOT / d).glob('*')):\n        if f.is_file():\n            on_disk.add(f'{d}/{f.name}')"
s = replace(s, old, 'on_disk = registered_files(ROOT, REGISTERED_DIRS)')
s = replace(s, "self_wf_files = sorted(f for f in SELF_WF_DIR.glob('*.yml') if f.is_file())", "self_wf_files = sorted(f for f in SELF_WF_DIR.iterdir() if f.is_file() and f.suffix in ('.yml', '.yaml'))")
s = replace(s, "if CONSUMER_SHARED_CALL in f.read_text(encoding='utf-8', errors='replace'))", "if shared_calls(f.read_text(encoding='utf-8', errors='replace')))")
s = replace(s, "'patch-yaml-shape.yml'],", "'patch-yaml-shape.yml', 'patch-tracked-ignored.yml', 'split-acceptance.yml'],")
# Verify the actual helper code, including a nested file and a .yaml consumer.
tree = ast.parse(s)
namespace = {'datetime': datetime, 're': re}
for node in tree.body:
    if isinstance(node, ast.FunctionDef) and node.name in {'aware_readback', 'registered_files', 'shared_calls'}:
        exec(compile(ast.Module(body=[node], type_ignores=[]), '<production-helper>', 'exec'), namespace)
for raw in ['2026-09-07', '2026-09-07T00:00:00', 1, None, '2026-02-30T00:00:00Z']:
    try:
        namespace['aware_readback'](raw)
        raise AssertionError('invalid date accepted')
    except ValueError:
        pass
assert namespace['aware_readback']('2026-09-07T00:00:00Z').tzinfo is not None
with tempfile.TemporaryDirectory() as d:
    r = Path(d); (r/'docs/nested').mkdir(parents=True); (r/'docs/nested/file.md').write_text('x')
    assert namespace['registered_files'](r, ['docs']) == {'docs/nested/file.md'}
assert namespace['shared_calls']('  uses: supercubegame/ci-workflows/.github/workflows/report.yml@main')
assert not namespace['shared_calls']('# uses: supercubegame/ci-workflows/.github/workflows/report.yml@main')
assert not namespace['shared_calls']("  run: echo 'uses: supercubegame/ci-workflows/.github/workflows/report.yml@main'")
p.write_text(s)

p = ROOT/'scripts/attest_delivery.py'; a = p.read_text()
a = replace(a, "first = body.lstrip('\\n').split('\\n', 1)[0].strip()", "first = body.split('\\n', 1)[0].removesuffix('\\r')")
a = replace(a, 'if first == marker:', "if first == marker and c.get('user', {}).get('id') == 41898282 and c.get('user', {}).get('login') == 'github-actions[bot]':")
a = replace(a, 'def evaluate(marker, sha, run_id, pr_number, pr_comments, commit_comments):', 'def evaluate(marker, sha, run_id, pr_number, pr_comments, commit_comments, repo=None, run_attempt=None):')
a = replace(a, "        body = hit[0].get('body') or ''\n", "        body = hit[0].get('body') or ''\n        if repo is not None:\n            identity = f'<!-- ci-report-execution:{repo}:{sha}:{run_id}:{run_attempt} -->'\n            if identity not in body.splitlines()[:2]:\n                problems.append('Current repository/SHA/run/attempt identity is missing or stale')\n")
a = replace(a, "        problems, _ = evaluate(marker, sha, run_id, None, prc, cc)", "        for comment in prc + cc:\n            comment.setdefault('user', {'id': 41898282, 'login': 'github-actions[bot]'})\n        problems, _ = evaluate(marker, sha, run_id, None, prc, cc)")
extra = '''    good[0]['user'] = {'id': 41898282, 'login': 'github-actions[bot]'}
    identity = f'<!-- ci-report-execution:owner/repo:{sha}:{run_id}:2 -->'
    current = dict(good[0], body=good_body.replace(marker+'\\n', marker+'\\n'+identity+'\\n'))
    if evaluate(marker, sha, run_id, None, [], [current], 'owner/repo', '2')[0]:
        broken.append('current identity positive control failed')
    for item, attempt in [(dict(current, user={'id': 1, 'login': 'github-actions[bot]'}), '2'),
                          (current, '3'), (dict(current, body='\\n'+current['body']), '2')]:
        if not evaluate(marker, sha, run_id, None, [], [item], 'owner/repo', attempt)[0]:
            broken.append('ownership/attempt/first-line negative was accepted')
    SELFTEST_CASE_COUNT += 4
'''
a = replace(a, '    return broken\n', extra + '    return broken\n')
page_helper = '''def api_pages(pathname, token):
    out = []
    for page in range(1, 101):
        batch = api(pathname + ('&' if '?' in pathname else '?') + f'per_page=100&page={page}', token)
        if not isinstance(batch, list):
            raise ValueError('paginated endpoint did not return a list')
        out.extend(batch)
        if len(batch) < 100:
            return out
    raise ValueError('pagination incomplete after 100 pages; not a clean result')


'''
a = replace(a, 'def main():\n', page_helper+'def main():\n')
a = replace(a, "pulls = api(f'/repos/{repo}/commits/{sha}/pulls', token)", "pulls = api_pages(f'/repos/{repo}/commits/{sha}/pulls', token)")
a = replace(a, "open_pr = next((p for p in pulls if p.get('state') == 'open'), None)", "event = json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text()) if os.environ.get('GITHUB_EVENT_PATH') else {}\n            event_pr = event.get('pull_request')\n            head = event_pr['head']['sha'] if event_pr else sha\n            candidates = [p for p in pulls if p.get('state') == 'open' and p.get('head', {}).get('sha') == head and (not event_pr or p['number'] == event_pr['number'])]\n            if len(candidates) > 1:\n                raise ValueError('ambiguous current PR destination')\n            open_pr = candidates[0] if candidates else None")
a = replace(a, "api(f'/repos/{repo}/issues/{pr_number}/comments?per_page=100', token)", "api_pages(f'/repos/{repo}/issues/{pr_number}/comments', token)")
a = replace(a, "api(f'/repos/{repo}/commits/{sha}/comments?per_page=100', token)", "api_pages(f'/repos/{repo}/commits/{sha}/comments', token)")
a = replace(a, 'evaluate(marker, sha, run_id, pr_number, pr_comments, commit_comments)', "evaluate(marker, sha, run_id, pr_number, pr_comments, commit_comments, repo, os.environ.get('GITHUB_RUN_ATTEMPT'))")
p.write_text(a)
ns = {'__name__': 'attest_test', '__file__': str(p)}; exec(compile(a,str(p),'exec'),ns)
assert not ns['selftest']()
# Production pagination implementation with fake pages, including the full-page boundary.
ns['api'] = lambda route, token: [{'id': i} for i in range(100)] if 'page=1' in route else [{'id':100}]
assert len(ns['api_pages']('/comments','unused')) == 101

# Read the exact public upstream revision, then verify Git's independent blob id.
upstream = '7ff526bfad7d6d7e055875574ccf8f686c6f7e48'
url = 'https://raw.githubusercontent.com/supercubegame/ci-workflows/'+upstream+'/.github/workflows/report.yml'
with urllib.request.urlopen(url, timeout=30) as response: raw = response.read()
assert blob(raw) == 'ccc30dbf35233ea80b8f0f664e3c608ae028fd42'
(ROOT/'vendor/ci-workflows/report.yml').write_bytes(raw)
m = json.loads((ROOT/'manifest.json').read_text()); before_limits = list(m['_tested_limits'])
copy = m['true_copies']['copies']['vendor/ci-workflows/report.yml']
copy.update(readback_at=datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),size_baseline_bytes=len(raw))
copy['source_commit'] = upstream
# Live readback at the beginning of this approved batch; content-level only, no raw rich-text claim.
for rel in ['agents/drift-devon.md','agents/gate-audit-quinn.md']:
    m['true_copies']['copies'][rel]['readback_at'] = '2026-09-07T05:02:00Z'
    m['true_copies']['copies'][rel]['readback_evidence'] = '2026-09-07 get_agent: name, description, schedule, triggers and full visible prompt compared with stored copy. Content-level equality, not raw rich-text byte identity. Live configuration unchanged.'
closure = '2026-09-07 audit closure of PR #106: the account holder reported deliberately deleting the independent skill in that incident. This explains the reported absence in that event only; it neither establishes nor rules out collateral deletion behavior elsewhere. No general platform deletion guarantee was tested.'
if closure not in m['_tested_limits']: m['_tested_limits'].append(closure)
assert m['_tested_limits'][:len(before_limits)] == before_limits
# Generate the existing consumer doc from the updated production renderer, without running the whole gate yet.
tree=ast.parse(s); names={'CONSUMER_FILES','expected_repo_count','expected_workflow_count'}; scope={}
for node in tree.body:
    if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id in names for t in node.targets):
        exec(compile(ast.Module(body=[node],type_ignores=[]),'<consumer-registry>','exec'),scope)
    if isinstance(node,ast.FunctionDef) and node.name=='render_consumers':
        exec(compile(ast.Module(body=[node],type_ignores=[]),'<consumer-renderer>','exec'),scope)
(ROOT/'docs/SHARED-WRITEBACK-CONSUMERS.md').write_text(scope['render_consumers']())
for rel in ['verify.py','scripts/attest_delivery.py','docs/SHARED-WRITEBACK-CONSUMERS.md','vendor/ci-workflows/report.yml','.github/workflows/maintenance.yml','repair_batch.py']:
    m['docs_integrity'][rel] = blob((ROOT/rel).read_bytes())
(ROOT/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
print('Approved maintenance: date/timezone, recursive registry, executable uses, pagination, owner/attempt, upstream bytes and evidence ledger updated. Original limits preserved.')
