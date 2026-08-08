#!/usr/bin/env python3
"""test_parse_anchor.py — presswire parse_plate 对照 latin parse_plate（任务 4/5 验收 + QA）

契约锚定（anchor）:
- golden fixtures: examples/plates/{p1,p2}.md 经 presswire parse_plate 的输出固化在
  tests/utils/golden/*.json（任务 5 起 presswire 为权威: 转义层从 LaTeX tex_escape
  迁移到 Typst 字符串安全转义，golden 也随之重生成）；断言后续输出与 golden 一致。
- 动态对照: 真实 daily plates 抽样 3 个，同时跑 presswire 与 latin 两个实现
  （latin 经 importlib 加载，不污染 sys.modules），逐键递归 diff；
  值比较先做**转义归一化**（latin LaTeX 转义 vs presswire Typst 转义 → 还原为原文），
  验证解析逻辑一致性而不被转义层差异误报。

用法:
    python3 tests/utils/test_parse_anchor.py        # 独立运行（退出码 0=全过）
    pytest tests/utils/test_parse_anchor.py         # pytest 收集
"""
import importlib.util
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import presswire.plates as pw_plates  # noqa: E402

LATIN_BUILD = Path.home() / 'news/latex/build.py'
EXAMPLES_DIR = Path.home() / 'news/latex/examples/plates'
DAILY_DIR = Path.home() / 'news/daily'
GOLDEN_DIR = Path(__file__).resolve().parent / 'golden'

# 真实样例抽样（固定路径，保证可重复；缺失时跳过该用例）
DAILY_SAMPLES = [
    '2026-08-05/plates/p3.md',
    '2026-08-06/plates/p1.md',
    '2026-08-06/plates/p4.md',
]


def latin_ref_available() -> bool:
    """latin 参考源（build.py + examples）是否可读。CI 无 → 跳过对照。"""
    return LATIN_BUILD.exists() and EXAMPLES_DIR.is_dir()


def load_latin_parse_plate():
    """importlib 加载 latin build.py → parse_plate 函数。"""
    spec = importlib.util.spec_from_file_location('latin_build_for_test', LATIN_BUILD)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.parse_plate


def latex_unescape(s: str) -> str:
    """latin tex_escape（build.py:52-74）的逆操作——还原为原文。

    对应关系（latin → 原文）: \\& → &、\\% → %、\\$ → $、\\# → #、\\_ → _、
    \\{ → {、\\} → }、\\textasciitilde{} → ~、\\textasciicircum{} → ^、
    \\textbackslash{} → \\、`` → “、'' → ”、\\textbf{x} → **x**、\\textit{x} → *x*。
    仅用于测试归一化（不是引擎代码）。
    """
    s = s.replace(r'\textasciitilde{}', '~').replace(r'\textasciicircum{}', '^')
    s = s.replace(r'\textbackslash{}', '\\')
    s = s.replace(r'\{', '{').replace(r'\}', '}').replace(r'\&', '&')
    s = s.replace(r'\%', '%').replace(r'\$', '$').replace(r'\#', '#').replace(r'\_', '_')
    s = s.replace('``', '“').replace("''", '”')
    s = re.sub(r'\\textbf\{([^}]*)\}', r'**\1**', s)
    s = re.sub(r'\\textit\{([^}]*)\}', r'*\1*', s)
    return s


def typst_unescape(s: str) -> str:
    """presswire Typst 转义的逆操作——还原为原文。

    对应关系（Typst → 原文）: \\\\ → \\、\\" → "（占位法保证顺序正确）。
    仅用于测试归一化（不是引擎代码）。
    """
    s = s.replace('\\\\', '\x00')   # 先占位所有 \\（反斜杠对）
    s = s.replace('\\"', '"')        # 再还原 \" → "
    return s.replace('\x00', '\\')   # 还原占位为单个反斜杠


def _same_after_unescape(pw, other, mode) -> bool:
    """值比较: 非字符串直接比；字符串先转义归一化（还原为原文）再比。

    mode='latin'（动态对照）: pw 用 typst_unescape，other 用 latex_unescape。
    mode='golden': 两边都是 presswire 输出，都用 typst_unescape。
    """
    if not isinstance(pw, str) or not isinstance(other, str):
        return pw == other
    pw2 = typst_unescape(pw)
    other2 = typst_unescape(other) if mode == 'golden' else latex_unescape(other)
    return pw2 == other2


def diff_dicts(pw, other, path='root', mode='latin') -> list:
    """递归逐键 diff 两个 dict（键集合/顺序 + 值）。返回差异行列表。

    值比较经转义归一化——mode='latin' 时（presswire Typst 转义 vs latin
    LaTeX 转义）；mode='golden' 时两边同为 presswire 输出。
    """
    diffs = []
    if type(pw) is not type(other):
        return [f'{path}: 类型不同 presswire={type(pw).__name__} other={type(other).__name__}']
    if isinstance(pw, dict):
        if list(pw.keys()) != list(other.keys()):
            diffs.append(f'{path}: 键集合/顺序不同\n    presswire={list(pw.keys())}\n    other    ={list(other.keys())}')
        for k in pw:
            diffs += diff_dicts(pw[k], other.get(k, '<缺失>'), f'{path}.{k}', mode)
        for k in set(other) - set(pw):
            diffs.append(f'{path}: other 独有键 {k!r}（presswire 缺失）')
    elif isinstance(pw, list):
        if len(pw) != len(other):
            diffs.append(f'{path}: 列表长度不同 presswire={len(pw)} other={len(other)}')
        for i, (a, b) in enumerate(zip(pw, other)):
            diffs += diff_dicts(a, b, f'{path}[{i}]', mode)
    elif not _same_after_unescape(pw, other, mode):
        diffs.append(f'{path}: 值不同（原文不一致）\n    presswire={pw!r}\n    other    ={other!r}')
    return diffs


def run_pair(name: str, md_path: Path, latin_parse, need_golden: bool) -> list:
    """对单个 plates 文件跑 presswire vs latin，返回差异行（空=一致）。"""
    text = md_path.read_text(encoding='utf-8')
    pw = pw_plates.parse_plate(text, filename=md_path.name)
    latin = latin_parse(text)
    diffs = diff_dicts(pw, latin)
    if need_golden:
        # golden fixtures: 固化 presswire 输出为 json（任务 5 起 presswire 为权威，
        # 转义层已是 Typst；latin 仅动态对照时做转义归一化）
        GOLDEN_DIR.mkdir(parents=True, exist_ok=True)
        golden_file = GOLDEN_DIR / f'{md_path.stem}.json'
        if not golden_file.exists():
            golden_file.write_text(
                json.dumps(pw, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
        golden = json.loads(golden_file.read_text(encoding='utf-8'))
        diffs += diff_dicts(pw, golden, f'{name}/golden', mode='golden')
    return diffs


def all_pairs(latin_parse) -> list:
    """组装全部对照用例: examples 2 个（golden）+ daily 抽样 3 个（动态）。"""
    pairs = []
    for md in sorted(EXAMPLES_DIR.glob('*.md')):
        pairs.append((f'examples/{md.name}', md, True))
    for rel in DAILY_SAMPLES:
        md = DAILY_DIR / rel
        if md.exists():
            pairs.append((f'daily/{rel}', md, False))
    return pairs


def test_examples_match_latin():
    """examples/plates/*.md: presswire 与 latin 输出一致（golden 锚定）。"""
    latin_parse = load_latin_parse_plate()
    failures = 0
    for name, md, need_golden in all_pairs(latin_parse):
        if not need_golden:
            continue
        diffs = run_pair(name, md, latin_parse, need_golden)
        assert not diffs, f'{name}: {len(diffs)} 处差异:\n' + '\n'.join(diffs)


def test_daily_samples_match_latin():
    """真实 daily plates 抽样: presswire 与 latin 输出一致（动态对照）。"""
    latin_parse = load_latin_parse_plate()
    failures = 0
    for name, md, need_golden in all_pairs(latin_parse):
        if need_golden:
            continue
        diffs = run_pair(name, md, latin_parse, need_golden)
        assert not diffs, f'{name}: {len(diffs)} 处差异:\n' + '\n'.join(diffs)


def main() -> int:
    # CI（GitHub Actions）无 /home/.../news/latex 参考源 → 标 [SKIP] 退出 0，
    # 不算失败（run_tests.py 按 "[SKIP]" 行归类）。本地路径存在则照常全跑。
    if not latin_ref_available():
        print('[SKIP] latin 参考源缺失（CI 环境），跳过对照测试')
        return 0
    latin_parse = load_latin_parse_plate()
    failures = 0
    pairs = all_pairs(latin_parse)
    if not pairs:
        print('FAIL: 未找到任何对照样例')
        return 1
    for name, md, need_golden in pairs:
        diffs = run_pair(name, md, latin_parse, need_golden)
        if diffs:
            failures += 1
            print(f'[FAIL] {name} ({md}) — {len(diffs)} 处差异:')
            for d in diffs[:10]:
                print(f'  {d}')
        else:
            tag = 'golden' if need_golden else 'diff'
            print(f'[PASS] {name} ({tag})')
    if failures:
        print(f'\n❌ {failures}/{len(pairs)} 项不一致')
        return 1
    print(f'\n✅ {len(pairs)} 项全部一致（presswire parse_plate ≡ latin parse_plate）')
    return 0


if __name__ == '__main__':
    sys.exit(main())
