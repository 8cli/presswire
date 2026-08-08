#!/usr/bin/env python3
"""test_autofit.py — 任务 11 QA: autofit 单次编译收敛（D3 债务消除）

验收（计划）: 对示例长文 plates，单次 typst compile 收敛；
溢出→收敛 / 太空→提升 / 边界→失败退出码 1。

断言方式:
- 溢出→收敛: 长文 plates（真实溢出 12%）autofit=true → compile 成功（无 panic）
- no-autofit: 同 plates → panic（严重溢出，CLI 退出码 1）
- 太空→不放大: 短内容 autofit=true → fill 不变（only-if-overflow 快速路径）

用法:
    python3 tests/test_autofit.py     # 独立运行（退出码 0=全过）
"""
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

TYPST_CLI = '/usr/local/bin/typst'
LATIN_PLATES = Path.home() / 'news/latex/examples/plates'  # 修复后不再溢出
OVERFLOW_PLATES = REPO_ROOT / 'tests' / 'fixtures' / 'overflow'
OUT_NAME = 'out-test-autofit'


def _gen(name: str, plates_dir, autofit: bool) -> Path:
    from presswire.render_typst import generate_typ
    text, _ = generate_typ(str(plates_dir))
    typ_path = REPO_ROOT / f'{name}.typ'
    typ_path.write_text(
        text.replace('#render-doc(plates)',
                     f'#render-doc(plates, autofit: {"true" if autofit else "false"})'),
        encoding='utf-8')
    return typ_path


def _cleanup():
    for suffix in ('.typ', '.pdf'):
        for name in (f'{OUT_NAME}-fit', f'{OUT_NAME}-nofit', f'{OUT_NAME}-short'):
            p = REPO_ROOT / f'{name}{suffix}'
            if p.exists():
                p.unlink()


def test_overflow_signals_article_mismatch():
    """溢出长文（12% 溢出）: autofit=true 字号固定 100% 不缩放 → 明确"文章
    不符合"信号（CLI 退出码 1 + framefit panic）。2026-08-08 用户决策:
    内容适配靠 imposer 选/改文章，不是字号缩放。"""
    typ = _gen(f'{OUT_NAME}-fit', OVERFLOW_PLATES, autofit=True)
    try:
        r = subprocess.run([TYPST_CLI, 'compile', str(typ), str(typ.with_suffix('.pdf'))],
                           capture_output=True, text=True)
        assert r.returncode == 1, f'超版心应报信号（不缩放）: {r.stderr[:200]}'
        # 2026-08-08 信号升级: fit-copy 废弃（text 包裹 grid 检测不可靠），
        # 溢出门禁归 plate-frame measure（severe-fill 1.0）→ "严重溢出" panic
        assert '严重溢出' in r.stderr, f'应 plate-frame 严重溢出 panic: {r.stderr[:200]}'
        # 不生成 PDF（超出即失败，imposer 选/改文章）
        assert not typ.with_suffix('.pdf').exists(), '超出不应出 PDF'
    finally:
        _cleanup()


def test_no_autofit_panics():
    """同长文 no-autofit → 严重溢出 panic（CLI 退出码 1）。"""
    typ = _gen(f'{OUT_NAME}-nofit', OVERFLOW_PLATES, autofit=False)
    try:
        r = subprocess.run([TYPST_CLI, 'compile', str(typ), str(typ.with_suffix('.pdf'))],
                           capture_output=True, text=True)
        assert 'panicked with' in r.stderr, f'应 panic: {r.stderr[:200]}'
        assert r.returncode == 1, f'panic 退出码应为 1: {r.returncode}'
    finally:
        _cleanup()


def test_short_content_not_scaled():
    """短内容: autofit=true 不放大（only-if-overflow: fill 不变）。"""
    import json
    typ = _gen(f'{OUT_NAME}-short', REPO_ROOT / 'tests' / 'fixtures' / 'layouts', autofit=True)
    try:
        r = subprocess.run([TYPST_CLI, 'compile', str(typ), str(typ.with_suffix('.pdf'))],
                           capture_output=True, text=True)
        assert r.returncode == 0, f'compile 失败: {r.stderr}'
        r = subprocess.run([TYPST_CLI, 'eval', 'query(metadata)', '--in', str(typ),
                            '--format', 'json'], capture_output=True, text=True)
        fills = [el['value']['fill'] for el in json.loads(r.stdout)]
        assert all(0 < f < 1 for f in fills), f'fill 应在 (0,1): {fills}'
    finally:
        _cleanup()


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
