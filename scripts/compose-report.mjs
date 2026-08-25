#!/usr/bin/env node
// ===========================================================================
// 把备份仓闸门的逐项结果合成一条评论。
//
// 契约由共享回写 workflow 定：`node scripts/compose-report.mjs reports` 写出
// comment.md；带 --check 时不写文件，只用退出码表示成败。
//
// **这个文件是这仓唯一的 JavaScript。** 闸门本体是 Python，而共享回写 workflow
// 用 `node <entry>` 调 composer —— 那是跨仓的契约，不是这仓的选择。
//
// **哨兵那一条是承重的。** 回写链路坏掉时，共享 workflow 会送一条「报告降级」
// 的兜底评论，那条评论**同样带着 marker**。所以「找到了带 marker 的评论」
// 这句话不能证明报告是完整的 —— attest 靠这个哨兵区分「composer 真跑过」和
// 「送出去的是兜底那份」。改这行字之前先看 scripts/attest_delivery.py。
// ===========================================================================
import fs from 'node:fs';
import path from 'node:path';

const COMPOSER_SENTINEL = '<!-- anyworkflow-composer-ran -->';
const LOG_TAIL_LINES = 80;
const GATE = { slug: 'backup', label: '备份仓闸门', file: 'verify-report.json' };

const args = process.argv.slice(2);
const dir = args.find(a => !a.startsWith('--')) || 'reports';
const checkOnly = args.includes('--check');

function walk(d, hits = []) {
  for (const ent of fs.readdirSync(d, { withFileTypes: true })) {
    const p = path.join(d, ent.name);
    if (ent.isDirectory()) walk(p, hits);
    else hits.push(p);
  }
  return hits;
}

function findFile(name) {
  try { return walk(dir).find(p => path.basename(p) === name) || null; }
  catch { return null; }
}

function tail(text, lines = LOG_TAIL_LINES) {
  return String(text || '').replace(/\s+$/, '').split('\n').slice(-lines).join('\n');
}

function fold(summary, text) {
  return '<details><summary>' + summary + '</summary>\n\n```\n' + text + '\n```\n\n</details>';
}

// ===========================================================================
// **把正文里的 HTML 注释开头拆开。这不是美化，是一个真事故的修法。**
//
// 闸门第 6 条（回写 marker 一致）的 detail 里带着 marker 原文。这个函数不在的时候，
// composer 会把它原样写进评论 —— **于是这条评论自己变成了 marker 查找的诱饵。**
//
// 平时看不见，因为只有一条报告评论，数到一条正好。但 run 32911142277 把 marker
// 改歪之后多出了第二条评论，而那条里同样印着 marker 原文。于是 attest 数到
// 两条，当场判「回写刷屏了」—— 而回写其实完全正常。
//
// 这是一条假红工厂：报告内容本身污染了那个用来找报告的标记。
// 同形的一条也写在 verify.yml 的 attest 日志回贴那一步里。
//
// **耦合参数**：marker 的形状（HTML 注释）和这一行拆法钉在一起。改 marker 的形状
// 就要重看这里。
// ===========================================================================
function defuse(text) {
  return String(text == null ? '' : text).replace(/<!--/g, '<! --');
}

const sha = (process.env.GITHUB_SHA || 'local').slice(0, 7);
const runLink = process.env.GITHUB_RUN_ID
  ? ' · [完整日志](' + (process.env.GITHUB_SERVER_URL || 'https://github.com') + '/' +
    (process.env.GITHUB_REPOSITORY || '') + '/actions/runs/' + process.env.GITHUB_RUN_ID + ')'
  : '';

const reportFile = findFile(GATE.file);
let data = null;
if (reportFile) {
  try { data = JSON.parse(fs.readFileSync(reportFile, 'utf8')); }
  catch (err) { data = null; }
}

let failed = false;
const sections = [];

if (!data || typeof data.total !== 'number') {
  // 「没有产出报告」只说明监控坏了，不说明为什么 —— 所以把 stdout 尾巴带上。
  failed = true;
  const logFile = findFile('stdout-' + GATE.slug + '.log');
  const log = logFile ? tail(fs.readFileSync(logFile, 'utf8')) : '';
  sections.push([
    '### ❌ ' + GATE.label + ' —— 没有产出报告',
    '',
    reportFile
      ? '报告文件在，但解析不出来。这算失败。'
      : '闸门在写出报告之前就崩了，或者 artifact 根本没上传。这算失败。',
    '',
    log ? fold('stdout 末尾 ' + LOG_TAIL_LINES + ' 行', defuse(log.slice(-8000)))
        : '连 stdout 也没拿到 —— 去看 workflow，不是看闸门。',
    ''
  ].join('\n'));
} else {
  const m = data.metrics || {};
  const failures = data.failures || [];
  if (data.passed !== data.total || failures.length) failed = true;
  sections.push([
    '### ' + (failed ? '❌' : '✅') + ' ' + GATE.label + ' —— ' + data.passed + '/' + data.total,
    '',
    ...(data.checks || []).map(c => '- ' + (c.ok ? '✅' : '❌') + ' ' + defuse(c.title) + ' — `' + defuse(c.detail) + '`'),
    '',
    '- 规矩文件: ' + m.rulesBytes + ' bytes（AGENTS.md 与 CLAUDE.md 逐字节相同）',
    '- 盲区清单: ' + m.notBackedUpCount + ' 条',
    '- manifest 顶层键: ' + JSON.stringify(m.manifestTopKeys),
    '- 回写 marker: `' + defuse(m.writebackMarker) + '` · 共享 workflow ref: `' + defuse(m.upstreamRef) + '`',
    ''
  ].join('\n'));
  if (failures.length) {
    sections.push(['### 失败项', '', ...failures.map(f => '- ' + defuse(f)), ''].join('\n'));
  }
}

const body = [
  COMPOSER_SENTINEL,
  '',
  failed ? '## 备份仓闸门有失败' : '## 备份仓闸门全部通过',
  '',
  (data && typeof data.total === 'number' ? data.passed + '/' + data.total + ' 项通过 · ' : '') +
    '提交 `' + sha + '`' + runLink,
  '',
  ...sections
].join('\n');

if (checkOnly) {
  const tally = data && typeof data.total === 'number' ? data.passed + '/' + data.total : 'no-report';
  process.stdout.write((failed ? 'FAILED' : 'PASSED') + ': ' + tally + '\n');
  process.exit(failed ? 1 : 0);
}

fs.writeFileSync('comment.md', body.slice(0, 60000));
process.stdout.write(body + '\n');
