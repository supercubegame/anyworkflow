"""Bounded observer fix; no live Agent changes or shared workflow changes."""
import ast,copy,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent
p=R/'scripts/attest_delivery.py';s=p.read_text()
def blob(b):return hashlib.sha1(b'blob %d\0'%len(b)+b).hexdigest()
def once(s,a,b):
 assert s.count(a)==1,a[:100]
 return s.replace(a,b,1)
if 'def select_delivery_pr(' not in s:
 assert blob(p.read_bytes())=='8fbc066716817c6bd8847743952f68bf62c78c19'
 a=s.index("            pulls = api_pages(f'/repos/{repo}/commits/{sha}/pulls', token)")
 z=s.index('            pr_number = open_pr.get',a)
 old=s[a:z]
 # Execute the exact old selection block with mock API + no event file:
 # then with a real temporary event file, proving the missing-association failure.
 import tempfile,os,textwrap
 with tempfile.TemporaryDirectory() as d:
  event_pr={'number':9,'state':'open','head':{'sha':'a'*40},'base':{'repo':{'full_name':'owner/repo'}}}
  event_file=Path(d)/'event.json';event_file.write_text(json.dumps({'pull_request':event_pr}))
  ns={'api_pages':lambda *x:[], 'repo':'owner/repo','sha':'b'*40,'token':'mock','json':json,'Path':Path,'os':type('Env',(),{'environ':{'GITHUB_EVENT_PATH':str(event_file)}})}
  exec(textwrap.dedent(old),ns)
  assert ns['open_pr'] is None
  print('BASELINE REPRODUCED: exact old observer selects commit when event PR exists but merge association is empty',flush=True)
 helper='''def select_delivery_pr(repo, sha, event, token, request=None, pages=None):
    """Independent observer: use current PR state, never infer absence from merge association."""
    request = request or api
    pages = pages or api_pages
    def valid_sha(value):
        return isinstance(value, str) and len(value) == 40 and all(c in '0123456789abcdef' for c in value)
    def valid_pr(value):
        return (isinstance(value, dict) and type(value.get('number')) is int and value['number'] > 0
                and value.get('state') in ('open', 'closed') and isinstance(value.get('head'), dict)
                and valid_sha(value['head'].get('sha')) and isinstance(value.get('base'), dict)
                and isinstance(value['base'].get('repo'), dict) and value['base']['repo'].get('full_name') == repo)
    if not isinstance(event, dict) or not valid_sha(sha):
        raise ValueError('invalid execution/event identity')
    event_pr = event.get('pull_request')
    if event_pr is not None:
        if not valid_pr(event_pr):
            raise ValueError('invalid event PR identity')
        current = request(f"/repos/{repo}/pulls/{event_pr['number']}", token)
        if not valid_pr(current) or current['number'] != event_pr['number']:
            raise ValueError('invalid current PR identity')
        if current['state'] == 'open' and current['head']['sha'] == event_pr['head']['sha']:
            return current
        return None  # Closed or newer head: do not demand an old report on the new PR state.
    pulls = pages(f'/repos/{repo}/commits/{sha}/pulls', token)
    if not isinstance(pulls, list) or any(not isinstance(item, dict) for item in pulls):
        raise ValueError('invalid association response')
    candidates = [item for item in pulls if valid_pr(item) and item['state'] == 'open' and item['head']['sha'] == sha]
    if len(candidates) > 1:
        raise ValueError('ambiguous current PR destination')
    return candidates[0] if candidates else None


def route_selftest():
    import copy
    repo, sha = 'owner/repo', 'a'*40
    pr = {'number':9,'state':'open','head':{'sha':sha},'base':{'repo':{'full_name':repo}}}
    def changed(**fields):
        result = copy.deepcopy(pr); result.update(fields); return result
    cases = [
        ('event with empty association', pr, pr, [], 9),
        ('event ignores unrelated association', pr, pr, [changed(number=10)], 9),
        ('closed current PR', pr, changed(state='closed'), [], None),
        ('newer head', pr, changed(head={'sha':'c'*40}), [], None),
        ('wrong current number', pr, changed(number=10), [], 'error'),
        ('wrong current repo', pr, changed(base={'repo':{'full_name':'other/repo'}}), [], 'error'),
        ('invalid current state', pr, changed(state='unknown'), [], 'error'),
        ('missing current head', pr, changed(head={}), [], 'error'),
        ('boolean event number', changed(number=True), pr, [], 'error'),
        ('non-PR association', None, pr, [pr], 9),
        ('non-PR no association', None, pr, [], None),
        ('non-PR ambiguity', None, pr, [pr, changed(number=10)], 'error'),
        ('non-PR foreign repo ignored', None, pr, [changed(base={'repo':{'full_name':'other/repo'}})], None),
        ('API error is not missing target', pr, 'api-error', [], 'error'),
    ]
    broken = []
    for label, event_pr, current, associated, want in cases:
        def request(route, token):
            if current == 'api-error': raise ValueError('mock API failure')
            if route != '/repos/owner/repo/pulls/9': raise AssertionError('wrong endpoint')
            return copy.deepcopy(current)
        def pages(route, token):
            if event_pr is not None: raise AssertionError('PR event must not depend on association list')
            return copy.deepcopy(associated)
        try:
            result = select_delivery_pr(repo, sha, {'pull_request':event_pr} if event_pr is not None else {}, 'mock', request, pages)
            got = result['number'] if result else None
        except ValueError:
            got = 'error'
        except Exception as err:
            broken.append(label+': unexpected '+str(err)); continue
        if got != want: broken.append(label+': expected '+str(want)+', got '+str(got))
    return broken, len(cases)


'''
 s=s[:a]+"            event = json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text()) if os.environ.get('GITHUB_EVENT_PATH') else {}\n            open_pr = select_delivery_pr(repo, sha, event, token)\n"+s[z:]
 s=once(s,'def main():\n',helper+'def main():\n')
 s=once(s,'    SELFTEST_CASE_COUNT += 4\n    return broken','    SELFTEST_CASE_COUNT += 4\n    route_broken, route_count = route_selftest()\n    broken.extend(route_broken)\n    SELFTEST_CASE_COUNT += route_count\n    return broken')
 p.write_text(s)
ns={'__name__':'observer_test','__file__':str(p)};exec(compile(s,str(p),'exec'),ns)
assert not ns['selftest'](),ns['selftest']()
print('OBSERVER SELFTEST',ns['SELFTEST_CASE_COUNT'],'passed; original 15 report checks and 14 route checks',flush=True)
# Keep old registry data and readback clocks unchanged; update only changed file digests.
mfile=R/'manifest.json';m=json.loads(mfile.read_text());before=copy.deepcopy(m)
for rel in ['scripts/attest_delivery.py','.github/workflows/maintenance.yml','repair_attest_route.py']:
 m['docs_integrity'][rel]=blob((R/rel).read_bytes())
assert m['true_copies']==before['true_copies'] and m['_tested_limits']==before['_tested_limits']
mfile.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
print('Integrity updated; Agent clocks, vendor copies and historical limits unchanged',flush=True)
