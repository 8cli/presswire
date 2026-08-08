#!/usr/bin/env python3
"""test_contract_shape.py — 任务 6 QA: demand/layout JSON 结构与 latin 一致（D2 红线）

验收标准: 对已知输入产生的 demand/layout JSON 与 latin build.py 字段结构相同。
对照方式: importlib 加载 latin build.py，相同输入跑两边，断言输出相等。

用法:
    python3 tests/test_contract_shape.py     # 独立运行（退出码 0=全过）
    pytest tests/test_contract_shape.py      # pytest 收集
"""
import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from presswire import contracts as pw  # noqa: E402

LATIN_BUILD = Path.home() / 'news/latex/build.py'

# 样例: 4 版（P2 main-aside → multi）
SAMPLE_LAYOUTS = {'p1': 'single', 'p2': 'multi', 'p3': 'single', 'p4': 'single'}
SAMPLE_DOCOPTS = ['', 'paper=a3,landscape', 'paper=a3,plates=2',
                  'paper=a3,landscape,plates=2,columns=3']


def load_latin():
    spec = importlib.util.spec_from_file_location('latin_build_for_contract', LATIN_BUILD)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_layout_json_matches_latin():
    """layout.json 结构与 latin write_tex 输出逐字节一致（4 种 docopts）。"""
    latin = load_latin()
    for docopts in SAMPLE_DOCOPTS:
        with tempfile.TemporaryDirectory() as td:
            latin.write_tex(os.path.join(td, 'out.tex'), '% dummy',
                            dict(SAMPLE_LAYOUTS), docopts)
            latin_json = json.load(open(os.path.join(td, 'layout.json'), encoding='utf-8'))
        pw_json = pw.layout_json(SAMPLE_LAYOUTS, docopts)
        assert latin_json == pw_json, f'docopts={docopts!r}:\nlatin={latin_json}\npw   ={pw_json}'


def test_estimate_requests_matches_latin():
    """补稿需求估算与 latin estimate_requests 一致（fill × 版号矩阵）。"""
    latin = load_latin()
    for fill in (0.97, 0.95, 0.91, 0.8, 0.5, 0.31):
        for idx in (0, 1, 2, 3):
            assert latin.estimate_requests(fill, 700, idx) == \
                pw.estimate_requests(fill, 700, idx), \
                f'fill={fill} idx={idx}'


def test_demand_json_structure():
    """demand.json 结构符合 imposer 契约（SKILL.md:135-140）:
    {"plates": {"P3": {"fill", "deficit_pt", "requests": [{type,count,words,topic,min_kind}]}}}"""
    d = pw.build_demand({'P3': {'fill': 0.31, 'deficit_pt': 84.2}})
    assert d is not None
    p3 = d['plates']['P3']
    assert set(p3.keys()) == {'fill', 'deficit_pt', 'requests'}
    assert p3['fill'] == 0.31
    assert p3['deficit_pt'] == 84.2
    req = p3['requests'][0]
    assert set(req.keys()) == {'type', 'count', 'words', 'topic', 'min_kind'}
    # 规格映射: P3 → space 题材
    assert p3['requests'][0]['topic'] == 'space'
    assert p3['requests'][0]['min_kind'] == 'agency'


def test_demand_json_none_when_full():
    """全部达标 → None（latin write_demand 语义: 无需求不发单）。"""
    assert pw.build_demand({'P1': {'fill': 0.97, 'deficit_pt': 0.0}}) is None


def test_write_demand_roundtrip():
    """write_demand_json 写出 → 读回与 build_demand 结构一致。"""
    with tempfile.TemporaryDirectory() as td:
        path = pw.write_demand_json(td, {'P1': {'fill': 0.91, 'deficit_pt': 12.0}})
        assert path is not None
        assert json.load(open(path, encoding='utf-8')) == \
            pw.build_demand({'P1': {'fill': 0.91, 'deficit_pt': 12.0}})
        # 无需求 → None 且不写文件
        assert pw.write_demand_json(td, {'P1': {'fill': 0.97, 'deficit_pt': 0.0}}) is None


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
