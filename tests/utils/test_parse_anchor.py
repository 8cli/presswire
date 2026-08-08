#!/usr/bin/env python3
"""test_parse_anchor.py — presswire parse_plate 对照 latin parse_plate（任务 4 验收 + QA）

契约锚定（anchor）:
- golden fixtures: examples/plates/{p1,p2}.md 经 latin parse_plate 的输出固化在
  tests/utils/golden/*.json；断言 presswire 输出与 golden 一致（字段名/值/类型/顺序）。
- 动态对照: 真实 daily plates 抽样 3 个，同时跑 presswire 与 latin 两个实现
  （latin 经 importlib 加载，不污染 sys.modules），逐键递归 diff。

用法:
    python3 tests/utils/test_parse_anchor.py        # 独立运行（退出码 0=全过）
    pytest tests/utils/test_parse_anchor.py         # pytest 收集
"""
import importlib.util
import json
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


def diff_dicts(pw, latin, path='root') -> list:
    """递归逐键 diff 两个 dict（键集合/顺序 + 值）。返回差异行列表。"""
    diffs = []
    if type(pw) is not type(latin):
        return [f'{path}: 类型不同 presswire={type(pw).__name__} latin={type(latin).__name__}']
    if isinstance(pw, dict):
        if list(pw.keys()) != list(latin.keys()):
            diffs.append(f'{path}: 键集合/顺序不同\n    presswire={list(pw.keys())}\n    latin    ={list(latin.keys())}')
        for k in pw:
            diffs += diff_dicts(pw[k], latin.get(k, '<缺失>'), f'{path}.{k}')
        for k in set(latin) - set(pw):
            diffs.append(f'{path}: latin 独有键 {k!r}（presswire 缺失）')
    elif isinstance(pw, list):
        if len(pw) != len(latin):
            diffs.append(f'{path}: 列表长度不同 presswire={len(pw)} latin={len(latin)}')
        for i, (a, b) in enumerate(zip(pw, latin)):
            diffs += diff_dicts(a, b, f'{path}[{i}]')
    elif pw != latin:
        diffs.append(f'{path}: 值不同\n    presswire={pw!r}\n    latin    ={latin!r}')
    return diffs


def run_pair(name: str, md_path: Path, latin_parse, need_golden: bool) -> list:
    """对单个 plates 文件跑 presswire vs latin，返回差异行（空=一致）。"""
    text = md_path.read_text(encoding='utf-8')
    pw = pw_plates.parse_plate(text, filename=md_path.name)
    latin = latin_parse(text)
    diffs = diff_dicts(pw, latin)
    if need_golden:
        # golden fixtures: 固化 latin 输出为 json，与 presswire 输出双向校验
        GOLDEN_DIR.mkdir(parents=True, exist_ok=True)
        golden_file = GOLDEN_DIR / f'{md_path.stem}.json'
        if not golden_file.exists():
            golden_file.write_text(
                json.dumps(latin, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
        golden = json.loads(golden_file.read_text(encoding='utf-8'))
        diffs += diff_dicts(pw, golden, f'{name}/golden')
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
