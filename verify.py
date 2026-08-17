#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
manifest = json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8'))

checks = []

def check(title, ok, detail):
    checks.append((title, ok, detail))
    print(("PASS" if ok else "FAIL") + f"  {title} | {detail}")

agents = (ROOT / 'AGENTS.md').read_bytes()
claude = (ROOT / 'CLAUDE.md').read_bytes()
check('AGENTS.md 与 CLAUDE.md 逐字节相同', agents == claude, f'{len(agents)} bytes')

recovery_exists = (ROOT / 'docs' / 'RECOVERY.md').exists()
check('恢复说明存在', recovery_exists, 'docs/RECOVERY.md')

blind_exists = (ROOT / 'docs' / 'BLIND-SPOTS.md').exists()
check('盲区清单存在', blind_exists, 'docs/BLIND-SPOTS.md')

nonempty = isinstance(manifest.get('not_backed_up'), list) and len(manifest['not_backed_up']) > 0
check('not_backed_up 不是空数组', nonempty, f"count={len(manifest.get('not_backed_up', [])) if isinstance(manifest.get('not_backed_up'), list) else 'bad-type'}")

missing = [k for k in ['purpose','backed_up','not_backed_up','invariants'] if k not in manifest]
check('manifest 顶层键齐全', len(missing) == 0, 'missing=' + (','.join(missing) if missing else 'none'))

failed = sum(1 for _, ok, _ in checks if not ok)
print(f"\n共执行 {len(checks)} 条检查，通过 {len(checks)-failed}，失败 {failed}")
raise SystemExit(1 if failed else 0)
