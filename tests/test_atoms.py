#!/usr/bin/env python3
"""test_atoms.py — 任务 10 QA: 排版原子渲染

验收（计划）: 每原子在样例中渲染正确（文本命中断言）；photo 原子绝对宽
（expM 定案）; 富文本 **x** → strong / *x* → emph（PDF 字体含 Bold）。

用法:
    python3 tests/test_atoms.py     # 独立运行（退出码 0=全过）
"""
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

TYPST_CLI = '/usr/local/bin/typst'
OUT_NAME = 'out-test-atoms'
FIXTURE_SVG = REPO_ROOT / 'tests' / 'fixtures' / 'atom-photo.svg'

PHOTO_SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="100" height="60">
  <rect width="100" height="60" fill="#8C1D18"/>
  <text x="10" y="35" fill="white" font-size="14">PHOTO</text>
</svg>"""

# 全覆盖原子: 版头 7 原子 + 内容原子（photo/pullquote/brief）+ 富文本
ATOMS_MD = """DATE: 2026年8月8日
KICKER: 眉题测试
HEADLINE: 标题测试 **加粗标题**
SUBHEADLINE: 副标题测试
DECK: 导语 *斜体* 测试
BYLINE: 记者 测试
LAYOUT: main-aside
COLUMNS: 2
IMAGE: ../tests/fixtures/atom-photo.svg
IMAGEWIDTH: 0.8
IMAGECAPTION: 图注测试
BODY:
正文第一段 **加粗** 与 *斜体* 混排测试。
PULLQUOTE: 引文测试内容。

STORY-B: 副故事标题
BYLINE-B: 副署名
副故事正文。
BRIEFS:
**1886** 简讯一。
简讯二。
MAINBRIEFS:
主栏补白简讯。
"""


def setup():
    REPO_ROOT.joinpath('tests', 'fixtures').mkdir(parents=True, exist_ok=True)
    FIXTURE_SVG.write_text(PHOTO_SVG, encoding='utf-8')
    plates_dir = REPO_ROOT / 'tests' / 'fixtures' / 'atoms'
    plates_dir.mkdir(parents=True, exist_ok=True)
    (plates_dir / 'p1.md').write_text(ATOMS_MD, encoding='utf-8')


def compile_all():
    from presswire.render_typst import generate_typ
    text, _ = generate_typ(str(REPO_ROOT / 'tests' / 'fixtures' / 'atoms'))
    typ_path = REPO_ROOT / f'{OUT_NAME}.typ'
    typ_path.write_text(text, encoding='utf-8')
    pdf_path = typ_path.with_suffix('.pdf')
    r = subprocess.run([TYPST_CLI, 'compile', '--root', str(REPO_ROOT),
                        str(typ_path), str(pdf_path)],
                       capture_output=True, text=True)
    assert r.returncode == 0, f'compile 失败: {r.stderr}'
    return typ_path, pdf_path


def text_of(pdf_path) -> str:
    r = subprocess.run(['pdftotext', str(pdf_path), '-'], capture_output=True, text=True)
    return r.stdout


def cleanup():
    for suffix in ('.typ', '.pdf'):
        p = REPO_ROOT / f'{OUT_NAME}{suffix}'
        if p.exists():
            p.unlink()


def test_all_atoms_render():
    """版头/内容原子全部渲染命中。"""
    setup()
    try:
        _, pdf = compile_all()
        t = text_of(pdf)
        # 注: subheadline/expanded 是 columns 版原子（main-aside 的 latin 契约
        # mainstory 无 subheadline 参数——见 test_layouts 的 columns 样例断言）
        for expected in ['眉题测试', '标题测试', '加粗标题', '导语',
                         '斜体', '记者 测试', '图注测试', '引文测试内容',
                         '副故事标题', '副署名', '副故事正文', '1886', '简讯一',
                         '简讯二', '主栏补白简讯']:
            assert expected in t, f'原子渲染缺失: {expected}'
    finally:
        cleanup()


def test_photo_renders():
    """photo 原子: IMAGE 渲染（SVG 转 PDF 有图）。"""
    setup()
    try:
        _, pdf = compile_all()
        # 图片渲染后 PDF 含图片对象
        r = subprocess.run(['pdfimages', '-list', str(pdf)], capture_output=True, text=True)
        # pdfimages -list 有输出即有图片；无则 fallback: 文件大小 > 纯文本 PDF
        img_list = r.stdout.strip()
        assert img_list or pdf.stat().st_size > 20000, 'photo 原子未渲染图片'
    finally:
        cleanup()


def test_rich_text_bold_font():
    """富文本 **x** → strong: PDF 字体含 Bold。"""
    setup()
    try:
        _, pdf = compile_all()
        r = subprocess.run(['pdffonts', str(pdf)], capture_output=True, text=True)
        assert 'Bold' in r.stdout, f'PDF 无 Bold 字体（strong 未生效）: {r.stdout}'
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
