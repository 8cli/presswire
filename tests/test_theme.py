#!/usr/bin/env python3
"""test_theme.py — 任务 9 QA: 主题预设（broadsheet 默认 + magazine）

验收（计划）: `--theme magazine` 编译出 PDF；主题 accent 色生效。

断言方式: 编译两主题 → 渲染首页 → 像素统计非灰主色（accent 文本色）：
broadsheet ≈ 深红 #8C1D18；magazine ≈ 深蓝 #1B3A5C。

用法:
    python3 tests/test_theme.py     # 独立运行（退出码 0=全过）
"""
import subprocess
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

TYPST_CLI = '/usr/local/bin/typst'
FIXTURES = REPO_ROOT / 'tests' / 'fixtures' / 'layouts'
OUT_NAME = 'out-test-theme'


def compile_theme(theme: str) -> Path:
    from presswire.render_typst import generate_typ
    text, _ = generate_typ(str(FIXTURES))
    typ_path = REPO_ROOT / f'{OUT_NAME}-{theme}.typ'
    typ_path.write_text(
        text.replace('#render-doc(plates)', f'#render-doc(plates, theme: "{theme}")'),
        encoding='utf-8')
    pdf_path = typ_path.with_suffix('.pdf')
    r = subprocess.run([TYPST_CLI, 'compile', str(typ_path), str(pdf_path)],
                       capture_output=True, text=True)
    assert r.returncode == 0, f'{theme} compile 失败: {r.stderr}'
    return pdf_path


def dominant_accent(pdf_path: Path) -> tuple:
    """渲染首页 → 非灰像素量化主色。"""
    import subprocess as sp
    png = pdf_path.with_suffix('.png')
    sp.run(['pdftoppm', '-f', '1', '-l', '1', '-r', '72', '-png', str(pdf_path), str(png)],
           capture_output=True)
    from PIL import Image
    png_page = Path(str(png) + '-1.png')
    img = Image.open(png_page).convert('RGB')
    colors = Counter()
    for px in img.get_flattened_data():
        r, g, b = px
        if max(r, g, b) - min(r, g, b) > 30:  # 排除近灰/黑白
            colors[(r // 32 * 32, g // 32 * 32, b // 32 * 32)] += 1
    img.close()
    png_page.unlink()
    return colors.most_common(1)[0][0] if colors else (0, 0, 0)


def cleanup():
    for theme in ('broadsheet', 'magazine'):
        for suffix in ('.typ', '.pdf'):
            p = REPO_ROOT / f'{OUT_NAME}-{theme}{suffix}'
            if p.exists():
                p.unlink()


def test_magazine_compiles():
    """magazine 主题编译出 PDF。"""
    try:
        pdf = compile_theme('magazine')
        assert pdf.exists() and pdf.stat().st_size > 1000
    finally:
        cleanup()


def test_broadsheet_accent_red():
    """broadsheet 默认主题 accent = 深红（R 显著高于 B）。"""
    try:
        pdf = compile_theme('broadsheet')
        r, g, b = dominant_accent(pdf)
        assert r > b + 40, f'broadsheet accent 应为深红: ({r},{g},{b})'
    finally:
        cleanup()


def test_magazine_accent_blue():
    """magazine 主题 accent = 深蓝（B 显著高于 R）。"""
    try:
        pdf = compile_theme('magazine')
        r, g, b = dominant_accent(pdf)
        assert b > r + 40, f'magazine accent 应为深蓝: ({r},{g},{b})'
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
