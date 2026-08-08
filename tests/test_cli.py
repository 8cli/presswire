#!/usr/bin/env python3
"""test_cli.py — 任务 16 QA: CLI 完整接入（D2 契约面）

验收（计划）: 解析 docopts（同 latin parse_docopts）且套字串一致；
黄金路径输出 out.pdf/out.log/layout.json/demand.json。

断言方式:
- 黄金路径: cli 跑通 → out.pdf + layout.json（sheets/layout 结构）+ demand.json
- 参数矩阵: --theme magazine / --no-autofit / plates=1 / 双版 plates=2

用法:
    python3 tests/test_cli.py     # 独立运行（退出码 0=全过）
"""
import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

PLATES = REPO_ROOT / 'tests' / 'fixtures' / 'layouts'


TMP_OUT = REPO_ROOT / 'tests' / 'tmp-out-cli'


def run_cli(docopts: str = 'paper=a3,landscape,plates=2,columns=3', extra=None) -> dict:
    # output 必须在仓库根内（Typst 沙箱 + 模板资产访问，同 latin 引擎目录先例）
    TMP_OUT.mkdir(parents=True, exist_ok=True)
    out = str(TMP_OUT / 'out.pdf')
    cmd = [sys.executable, '-m', 'presswire.cli', str(PLATES), out,
           '--docopts', docopts]
    if extra:
        cmd += extra
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_ROOT)
    return {'code': r.returncode, 'stdout': r.stdout, 'stderr': r.stderr,
            'dir': str(TMP_OUT), 'out': out}


def _cleanup_tmp():
    import shutil
    shutil.rmtree(TMP_OUT, ignore_errors=True)


def test_golden_path():
    """黄金路径: PDF + layout.json + demand.json 全部产出。"""
    res = run_cli(extra=['--demand'])
    assert res['code'] == 0, f'CLI 失败: {res["stderr"]}'
    td = res['dir']
    assert os.path.exists(res['out']), 'out.pdf 未生成'
    layout = json.load(open(os.path.join(td, 'layout.json'), encoding='utf-8'))
    assert 'sheets' in layout and 'layout' in layout
    assert layout['layout']['p1'] == 'multi', 'P1 应 main-aside → multi'
    assert json.load(open(os.path.join(td, 'demand.json'), encoding='utf-8')), 'demand.json 缺失'


def test_theme_magazine():
    """--theme magazine → render-doc theme 参数生效（编译通过）。"""
    res = run_cli(docopts='paper=a3,landscape,plates=2,columns=3,theme=magazine')
    assert res['code'] == 0, f'magazine 失败: {res["stderr"]}'


def test_no_autofit():
    """--no-autofit: 编译成功（短内容不 panic）。"""
    res = run_cli(extra=['--no-autofit'])
    assert res['code'] == 0, f'--no-autofit 失败: {res["stderr"]}'


def test_dual_plate_layout_json():
    """plates=2: layout.json sheets 分页（2 版 → front）。"""
    res = run_cli()
    assert res['code'] == 0
    td = res['dir']
    layout = json.load(open(os.path.join(td, 'layout.json'), encoding='utf-8'))
    assert layout['sheets']['front'] == ['p1', 'p2'], layout['sheets']


if __name__ == '__main__':
    _cleanup_tmp()
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
    _cleanup_tmp()
    sys.exit(1 if failures else 0)
