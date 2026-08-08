#!/usr/bin/env python3
"""test_demand.py — 任务 17 QA: overflow.py 溢出报告 + demand 组装

验收（计划）: 长文 plates → demand.json 请求符合 fill_min 语义；
measure 对比模式（plate-frame）+ eval 全量取回 → Python 按 label 分组。

断言方式:
- read_fills: 编译 fixture → eval 取 fill/deficit/overflow（deficit_pt 字符串化）
- plates_fill_demand: deficit_pt 契约换算（latin 语义）
- demand.json 结构（contracts 冻结）: {"plates": {P1: {fill, deficit_pt, requests}}}

用法:
    python3 tests/test_demand.py     # 独立运行（退出码 0=全过）
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

TYPST_CLI = '/usr/local/bin/typst'
FIXTURES = REPO_ROOT / 'tests' / 'fixtures' / 'layouts'
OUT_NAME = 'out-test-demand'


def gen_and_compile() -> Path:
    from presswire.render_typst import generate_typ
    text, _ = generate_typ(str(FIXTURES))
    typ_path = REPO_ROOT / f'{OUT_NAME}.typ'
    typ_path.write_text(text, encoding='utf-8')
    r = subprocess.run([TYPST_CLI, 'compile', str(typ_path), str(typ_path.with_suffix('.pdf'))],
                       capture_output=True, text=True)
    assert r.returncode == 0, f'compile 失败: {r.stderr[:200]}'
    return typ_path


def cleanup():
    for suffix in ('.typ', '.pdf'):
        p = REPO_ROOT / f'{OUT_NAME}{suffix}'
        if p.exists():
            p.unlink()


def test_read_fills():
    """read_fills: eval 全量取回（label 分组）+ deficit_pt 字符串化处理。"""
    from presswire.overflow import read_fills
    typ = gen_and_compile()
    try:
        fills = read_fills(str(typ), str(REPO_ROOT))
        assert 'plate-P1' in fills and 'plate-P2' in fills, f'label 分组缺失: {list(fills)}'
        f = fills['plate-P1']
        assert 0 < f['fill'] < 1, f'fill 异常: {f}'
        assert f['overflow'] is False
        assert isinstance(f['deficit_pt'], float), f'deficit_pt 应为 float: {f}'
    finally:
        cleanup()


def test_plates_fill_demand_contract():
    """plates_fill_demand: deficit_pt 契约换算（latin 语义）。"""
    from presswire.overflow import plates_fill_demand
    fills = {'plate-P1': {'fill': 0.228, 'deficit_pt': 571.0, 'overflow': False}}
    d = plates_fill_demand(fills)
    # deficit_pt = (0.95 − 0.228) × content_h，content_h = 571/(1−0.228)
    expected = round((0.95 - 0.228) * 571.0 / (1 - 0.228), 1)
    assert d['P1']['deficit_pt'] == expected, f'{d["P1"]["deficit_pt"]} != {expected}'


def test_demand_end_to_end():
    """端到端: cli --demand → demand.json 结构符合契约。"""
    from presswire import contracts
    from presswire.overflow import read_fills, plates_fill_demand
    typ = gen_and_compile()
    try:
        fills = read_fills(str(typ), str(REPO_ROOT))
        with tempfile.TemporaryDirectory() as td:
            dpath = contracts.write_demand_json(td, plates_fill_demand(fills))
            assert dpath is not None, 'fill < 0.95 应发补稿单'
            d = json.load(open(dpath, encoding='utf-8'))
            p1 = d['plates']['P1']
            assert set(p1.keys()) == {'fill', 'deficit_pt', 'requests'}
            req = p1['requests'][0]
            assert set(req.keys()) == {'type', 'count', 'words', 'topic', 'min_kind'}
    finally:
        cleanup()


if __name__ == '__main__':
    import traceback
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith('test_') and callable(fn):
            try:
                fn()
                print(f'[PASS] {name}')
            except Exception:
                failures += 1
                print(f'[FAIL] {name}')
                traceback.print_exc()
    sys.exit(1 if failures else 0)
