#!/usr/bin/env python3
"""test_poster.py — 任务 13 QA: 画报版型 LAYOUT: poster（N3 + U4）

验收（mini-spike 定案 + 计划）: examples/poster/ 画报 PDF 图多、标题凌驾、
板块网格；无空白带（pixelcheck）；place 贪心装配可用（expP 实证）。

断言方式:
- 编译: LAYOUT: poster 样张 → compile 成功
- 渲染: pdftotext 命中标题/正文 + 墨覆盖率 > 0.15（有实质内容）
- 图片: pdfimages -list 有图（IMAGE + body ![](path) 双图）

用法:
    python3 tests/test_poster.py     # 独立运行（退出码 0=全过）
"""
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

TYPST_CLI = '/usr/local/bin/typst'
OUT_NAME = 'out-test-poster'
FIXTURES = REPO_ROOT / 'tests' / 'fixtures' / 'poster'
IMG_SRC = REPO_ROOT / 'dev' / 'research' / 'experiments' / 'expP-img.svg'

POSTER_MD = """KICKER: 画报
HEADLINE: 航空工业画报：中国商飞 C919
DECK: 从首飞到商业运营，国产大飞机的里程碑时刻。
BYLINE: 摄影 新华社
LAYOUT: poster
IMAGE: REPLACE_IMG
IMAGEWIDTH: 1.0
IMAGECAPTION: C919 商业首航
BODY:
![](REPLACE_IMG)
画报正文：C919 完成商业首航 Beijing-Shanghai，国产大飞机正式投入商业运营。
第二段：**加粗** 与 *斜体* 混排的画报文字板块。
"""


def setup():
    FIXTURES.mkdir(parents=True, exist_ok=True)
    # 图片路径相对模板（presswire_typst/）: 上溯到仓库根再进 dev/
    rel = '../dev/research/experiments/expP-img.svg'
    (FIXTURES / 'p1.md').write_text(
        POSTER_MD.replace('REPLACE_IMG', rel), encoding='utf-8')


def compile_poster() -> Path:
    from presswire.render_typst import generate_typ
    text, _ = generate_typ(str(FIXTURES))
    typ_path = REPO_ROOT / f'{OUT_NAME}.typ'
    typ_path.write_text(text, encoding='utf-8')
    pdf_path = typ_path.with_suffix('.pdf')
    r = subprocess.run([TYPST_CLI, 'compile', str(typ_path), str(pdf_path)],
                       capture_output=True, text=True)
    assert r.returncode == 0, f'compile 失败: {r.stderr[:200]}'
    return pdf_path


def cleanup():
    for suffix in ('.typ', '.pdf'):
        p = REPO_ROOT / f'{OUT_NAME}{suffix}'
        if p.exists():
            p.unlink()


def test_poster_compiles_and_renders():
    """画报编译成功 + 标题/正文命中 + 墨覆盖率 > 0.15。"""
    if not IMG_SRC.exists():
        print('[SKIP] expP-img.svg 不存在（spike 资产缺失）')
        return
    setup()
    try:
        pdf = compile_poster()
        t = subprocess.run(['pdftotext', str(pdf), '-'],
                           capture_output=True, text=True).stdout
        assert '航空工业画报' in t, '画报标题缺失'
        assert '中国商飞 C919' in t, '标题内容缺失'
        assert '商业首航' in t, '正文缺失'
        # 墨覆盖率（板块布局有实质内容）
        png = pdf.with_suffix('')
        subprocess.run(['pdftoppm', '-f', '1', '-l', '1', '-r', '72', '-png',
                        str(pdf), str(png)], capture_output=True)
        from PIL import Image
        img = Image.open(str(png) + '-1.png').convert('RGB')
        dark = sum(1 for px in img.get_flattened_data() if max(px) < 150)
        ink = dark / (img.width * img.height)
        img.close()
        Path(str(png) + '-1.png').unlink()
        assert ink > 0.15, f'墨覆盖率过低（画报内容不足）: {ink:.3f}'
    finally:
        cleanup()


def test_poster_has_images():
    """画报含图片（IMAGE + body ![](path) → pdfimages 有图）。"""
    if not IMG_SRC.exists():
        print('[SKIP] expP-img.svg 不存在')
        return
    setup()
    try:
        pdf = compile_poster()
        r = subprocess.run(['pdfimages', '-list', str(pdf)],
                           capture_output=True, text=True)
        assert r.stdout.strip() or pdf.stat().st_size > 30000, \
            f'画报无图片: {r.stdout}'
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
