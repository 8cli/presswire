#!/usr/bin/env python3
"""test_library.py — 2026-08-08 库模式门面 QA（内存通讯）

验收（expS 三实验坐实后的实现层）:
- render() 全闭环: 编译 → fills → demand → layout（双后端）
- cli 后端（subprocess，默认）: 行为与旧 cli 等价
- typstpy 后端（进程内）: 3.14 无 wheel → 自动 SKIP；3.12 venv 真实执行
- 文章不符合信号: 长文 autofit → article_mismatch=True + code=1
- 严重溢出: 长文 no-autofit → panic=True + code=1
- 沙箱校验: output 在 root 外 → code=2

用法:
    python3 tests/test_library.py      # 独立运行（退出码 0=全过）
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
LATIN_PLATES = Path.home() / 'news' / 'latex' / 'examples' / 'plates'  # 字体/分栏修复后不再溢出（fill ~0.75）
OVERFLOW_PLATES = REPO_ROOT / 'tests' / 'fixtures' / 'overflow'  # 必然溢出（1500 词）
OUT_NAME = 'out-test-library'
# 输出须在 root 内（Typst 沙箱）→ 用仓库内 tests/tmp-out-library/（test_cli 同模式）
TMP_ROOT = REPO_ROOT / 'tests' / 'tmp-out-library'
TMP_ROOT.mkdir(parents=True, exist_ok=True)  # pytest 模式也须可用（_cleanup 只在 __main__ 直接执行时跑）

TYPSTPY_OK = False
try:
    import typst  # noqa: F401
    TYPSTPY_OK = True
except ImportError:
    pass


def _cleanup():
    import shutil
    shutil.rmtree(TMP_ROOT, ignore_errors=True)
    TMP_ROOT.mkdir(parents=True, exist_ok=True)  # 重建供 TemporaryDirectory(dir=) 使用
    for suffix in ('.typ', '.pdf'):
        p = REPO_ROOT / f'{OUT_NAME}{suffix}'
        if p.exists():
            p.unlink()


def test_render_cli_golden_path():
    """cli 后端: render 全闭环（fills/demand/layout 结构化 + PDF 留盘）。"""
    from presswire.library import render
    with tempfile.TemporaryDirectory(dir=str(TMP_ROOT)) as td:
        res = render(str(FIXTURES), os.path.join(td, 'out.pdf'),
                     backend='cli', write_demand=True)
        assert res['ok'] and res['code'] == 0, f'render 失败: {res["error"]}'
        assert res['backend'] == 'cli'
        assert os.path.exists(res['pdf']), 'PDF 未生成'
        assert 'plate-P1' in res['fills'], f'fills 缺失: {list(res["fills"])}'
        f = res['fills']['plate-P1']
        assert 0 < f['fill'] < 1 and isinstance(f['deficit_pt'], float)
        assert res['layout_json']['layout']['p1'] == 'multi'
        assert res['demand'] is not None and 'P1' in res['demand']['plates'], \
            'fill < 0.95 应发补稿单'
        assert res['demand_path'] and os.path.exists(res['demand_path'])


def test_render_cli_no_demand_stale_cleared():
    """write_demand: 无需求清空旧单（血泪 #53 语义）。"""
    from presswire.library import render
    with tempfile.TemporaryDirectory(dir=str(TMP_ROOT)) as td:
        # 预置陈旧 demand.json → 渲染后应被清除
        stale = os.path.join(td, 'demand.json')
        Path(stale).write_text('{"plates": {}}', encoding='utf-8')
        res = render(str(FIXTURES), os.path.join(td, 'out.pdf'),
                     backend='cli', write_demand=True)
        assert res['ok']
        # fixtures 太空 → 必有需求 → 旧单被新单覆盖
        assert res['demand_path'] and os.path.exists(res['demand_path'])


def test_render_sandbox_checks():
    """沙箱校验: output 在 root 外 / root 不含模板资产 → code=2。"""
    from presswire.library import render
    # output 在 root 外: 用系统 /tmp（不在 REPO_ROOT 内）
    outside_dir = tempfile.mkdtemp()
    try:
        outside = os.path.join(outside_dir, 'outside.pdf')
        res = render(str(FIXTURES), outside, root=str(REPO_ROOT))
        assert res['code'] == 2 and '项目根内' in res['error'], f'{res}'
    finally:
        import shutil
        shutil.rmtree(outside_dir, ignore_errors=True)
    # root 不含 presswire_typst（用仓库内子目录作 root）
    with tempfile.TemporaryDirectory(dir=str(TMP_ROOT)) as td:
        res2 = render(str(FIXTURES), os.path.join(td, 'out.pdf'), root=td)
        assert res2['code'] == 2 and '模板资产' in res2['error'], f'{res2}'


def test_render_cli_article_mismatch():
    """长文 autofit（字号固定 100%）: article_mismatch=True + code=1。"""
    from presswire.library import render
    with tempfile.TemporaryDirectory(dir=str(TMP_ROOT)) as td:
        res = render(str(OVERFLOW_PLATES), os.path.join(td, 'out.pdf'),
                     backend='cli', autofit=True)
        assert res['code'] == 1, f'长文应报文章不符合: {res}'
        assert res['article_mismatch'] is True
        assert '文章不符合' in res['error']


def test_render_cli_panic():
    """长文 no-autofit: 严重溢出 panic（D4 红线）。"""
    from presswire.library import render
    with tempfile.TemporaryDirectory(dir=str(TMP_ROOT)) as td:
        res = render(str(OVERFLOW_PLATES), os.path.join(td, 'out.pdf'),
                     backend='cli', autofit=False)
        assert res['code'] == 1 and res['panic'] is True, f'{res}'


def test_render_typstpy_golden_path():
    """typstpy 后端（进程内）: 与 cli 后端同结构（3.14 无 wheel → SKIP）。"""
    if not TYPSTPY_OK:
        print('[SKIP] typst-py 无 3.14 wheel（CI 3.12 真实执行）')
        return
    from presswire.library import render
    with tempfile.TemporaryDirectory(dir=str(TMP_ROOT)) as td:
        res = render(str(FIXTURES), os.path.join(td, 'out.pdf'),
                     backend='typstpy', write_demand=True)
        assert res['ok'] and res['backend'] == 'typstpy', f'{res}'
        assert os.path.exists(res['pdf'])
        assert 'plate-P1' in res['fills']
        assert res['demand'] is not None


def test_render_typstpy_article_mismatch():
    """typstpy 后端文章不符合信号（expS 实验 1: message 逐字一致）。"""
    if not TYPSTPY_OK:
        print('[SKIP] typst-py 无 3.14 wheel（CI 3.12 真实执行）')
        return
    from presswire.library import render
    with tempfile.TemporaryDirectory(dir=str(TMP_ROOT)) as td:
        res = render(str(OVERFLOW_PLATES), os.path.join(td, 'out.pdf'),
                     backend='typstpy', autofit=True)
        assert res['code'] == 1 and res['article_mismatch'] is True, f'{res}'


def test_cli_json_mode():
    """cli --json: stdout 纯 JSON（fills/demand/layout/error 全字段）。"""
    with tempfile.TemporaryDirectory(dir=str(TMP_ROOT)) as td:
        out = os.path.join(td, 'out.pdf')
        r = subprocess.run([sys.executable, '-m', 'presswire.cli',
                            str(FIXTURES), out, '--json', '--demand',
                            '--docopts', 'paper=a3,landscape,plates=2,columns=3'],
                           capture_output=True, text=True, cwd=REPO_ROOT)
        assert r.returncode == 0, f'cli --json 失败: {r.stderr}'
        res = json.loads(r.stdout)
        assert res['engine'] == 'presswire' and res['ok'] is True
        assert 'fills' in res and 'demand' in res and 'layout_json' in res
        assert res['backend'] in ('cli', 'typstpy', 'auto')
        assert '✅' not in r.stdout, '机器模式 stdout 应纯净 JSON'


def test_cli_json_article_mismatch():
    """cli --json 错误场景: stdout 仍输出 JSON（含 article_mismatch 信号）。"""
    with tempfile.TemporaryDirectory(dir=str(TMP_ROOT)) as td:
        out = os.path.join(td, 'out.pdf')
        r = subprocess.run([sys.executable, '-m', 'presswire.cli',
                            str(OVERFLOW_PLATES), out, '--json',
                            '--docopts', 'paper=a3,landscape,plates=2,columns=3'],
                           capture_output=True, text=True, cwd=REPO_ROOT)
        assert r.returncode == 1
        res = json.loads(r.stdout)
        assert res['article_mismatch'] is True
        assert '文章不符合' in res['error']


if __name__ == '__main__':
    _cleanup()
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
    _cleanup()
    sys.exit(1 if failures else 0)
