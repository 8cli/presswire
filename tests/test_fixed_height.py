#!/usr/bin/env python3
"""test_fixed_height.py — 任务 7 QA: 固定版心 + 溢出报告 + D4 红线

验收（计划）:
- positive 满格: 读 plates → typst compile 出 PDF 且 fill < 1 / overflow=False，
  eval 'query(metadata)' 能取 fill/deficit（P0 通道）。
- negative 溢出: 超长版 → 严重溢出（fill > 1.05）→ typst-py compile() 抛
  TypstError（D4 红线: CLI 退出码 0 不可靠，必须 Python 捕获 → sys.exit(1)）。

注意: 本机 Python 3.14 无 typst wheel——negative 用例在 import typst 失败时 SKIP；
CI（3.12）会真实执行。

用法:
    python3 tests/test_fixed_height.py     # 独立运行（退出码 0=全过）
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

LATIN_PLATES = Path.home() / 'news/latex/examples/plates'
TYPST_CLI = '/usr/local/bin/typst'


def _gen_typ(name: str, body_paras: list) -> Path:
    """在仓库根生成临时 .typ（模板相对路径依赖 cwd=仓库根），返回路径。"""
    body = '", "'.join(body_paras)
    path = REPO_ROOT / f'{name}.typ'
    path.write_text(
        '#import "presswire_typst/presswire.typ": render-doc\n'
        '#let p = (\n'
        '  "kicker": "", "headline": "固定版心测试", "subheadline": "", "deck": "",\n'
        '  "byline": "", "date": "", "body": ("' + body + '",),\n'
        '  "pullquote": "", "briefs": (), "mainbriefs": (), "stories": (),\n'
        '  "layout": "", "columns": "", "expanded": "", "image": "",\n'
        '  "imagewidth": "1.0", "imagecaption": "",\n'
        ')\n#let plates = (p,)\n#render-doc(plates)\n',
        encoding='utf-8')
    return path


def _cleanup(path: Path):
    for suffix in ('.typ', '.pdf'):
        p = path.with_suffix(suffix)
        if p.exists():
            p.unlink()


def test_positive_fill():
    """满格（短内容）: compile 出 PDF + eval 取 fill < 1 / overflow=False。"""
    typ = _gen_typ('out-test-pos', ['第一段正常内容。', '第二段正常内容。'])
    try:
        r = subprocess.run([TYPST_CLI, 'compile', str(typ), str(typ.with_suffix('.pdf'))],
                           capture_output=True, text=True)
        assert r.returncode == 0, f'compile 失败: {r.stderr}'
        assert typ.with_suffix('.pdf').exists(), 'PDF 未生成'

        r = subprocess.run(
            [TYPST_CLI, 'eval', 'query(metadata)', '--in', str(typ), '--format', 'json'],
            capture_output=True, text=True)
        assert r.returncode == 0, f'eval 失败: {r.stderr}'
        data = json.loads(r.stdout)
        assert data, '无 metadata 返回'
        v = data[0]['value']
        assert v['overflow'] is False, '短内容不应溢出'
        assert 0 < v['fill'] < 1, f"fill 应在 (0,1): {v['fill']}"
        # deficit_pt 为 length → JSON 字符串化（计划注意点）
        assert isinstance(v['deficit_pt'], str) and v['deficit_pt'].endswith('pt'), \
            f"deficit_pt 应为 '...pt' 字符串: {v['deficit_pt']!r}"
    finally:
        _cleanup(typ)


def test_negative_severe_overflow():
    """严重溢出: typst-py compile() 抛 TypstError（D4 红线；CLI 退出码 0 不可靠）。"""
    try:
        import typst
    except ImportError:
        print('[SKIP] typst-py 不可用（本机 3.14 无 wheel；CI 3.12 真实执行）')
        return

    long_para = '这是一段很长的中文正文，用来撑爆固定版心。' * 60
    typ = _gen_typ('out-test-neg', [long_para] * 20)
    try:
        raised = False
        try:
            typst.compile(str(typ))
        except typst.TypstError:
            raised = True
        assert raised, '严重溢出未抛 TypstError（D4 红线失效）'
    finally:
        _cleanup(typ)


def test_cli_panic_exit_code():
    """D4 红线实证: CLI 遇 panic 退出码为 1（0.15.1 无管道精确测量）。

    2026-08-08 修正: 早前"退出码 0"记录来自管道测量错误（`| head` 使 $? 变
    head 退出码）。精确测量（subprocess 无管道）: panic 退出码 = 1。
    但 QA 门禁仍用 typst-py 捕获——CLI 只能靠退出码/stderr 文本判断，
    typst-py 得结构化 TypstError + 同进程可继续 eval query（任务 17）。
    """
    long_para = '这是一段很长的中文正文，用来撑爆固定版心。' * 60
    typ = _gen_typ('out-test-panic', [long_para] * 20)
    try:
        r = subprocess.run([TYPST_CLI, 'compile', str(typ), str(typ.with_suffix('.pdf'))],
                           capture_output=True, text=True)
        assert 'panicked with' in r.stderr or 'panicked' in r.stderr, \
            f'应 panic: {r.stderr}'
        assert r.returncode == 1, f'CLI panic 退出码应为 1: {r.returncode}'
    finally:
        _cleanup(typ)


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
