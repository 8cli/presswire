#!/usr/bin/env python3
"""test_layouts.py — 任务 8 QA: main-aside / columns 版式渲染

验收（计划）: 示例 P1 两栏 + 侧栏 + 补白，P2 等宽；每个版式一个 PDF + 结构断言。

断言方式: 编译后 pdftotext 提取文本，验证各版式关键字段命中 +
页数正确（1 版 1 页，无尾随空页）+ eval fill 报告正常。

用法:
    python3 tests/test_layouts.py     # 独立运行（退出码 0=全过）
"""
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

TYPST_CLI = '/usr/local/bin/typst'
TEST_PLATES = REPO_ROOT / 'tests' / 'fixtures' / 'layouts'
OUT_NAME = 'out-test-layouts'

# main-aside 样例（P1）: 主栏 + 侧栏 + 主栏补白 + IN BRIEF
MAINASIDE_MD = """DATE: 2026年8月8日
KICKER: 头版
HEADLINE: 主栏标题：中英混排测试
DECK: 这是导语段，测试 main-aside 版式的主栏与侧栏结构。
BYLINE: 记者 张三
LAYOUT: main-aside
COLUMNS: 2
BODY:
主栏第一段正文。Main column body text for the main story.
主栏第二段，测试两栏分栏效果与列平衡行为。

STORY-B: 侧栏故事一
BYLINE-B: 记者 李四
侧栏故事正文，测试侧栏渲染。

STORY-C: 侧栏故事二
侧栏故事二正文内容。

BRIEFS:
简讯一条：内容简介。
简讯二条：简短内容。
MAINBRIEFS:
主栏补白：底部简讯。
"""

# columns 样例（P2）: 等宽 3 栏 + 引文 + 栏内副故事 + IN BRIEF（4 条 → 2 组）
COLUMNS_MD = """KICKER: 国际
HEADLINE: 等宽多栏版测试标题
SUBHEADLINE: 副标题一行
DECK: 导语段内容。
BYLINE: 记者 王五
COLUMNS: 3
BODY:
等宽三栏正文第一段。Column one text content.
等宽三栏正文第二段内容，测试多栏分栏。
PULLQUOTE: 引文内容测试。

STORY-B: 栏内副故事
栏内副故事正文。

BRIEFS:
简讯甲。
简讯乙。
简讯丙。
简讯丁。
"""


def setup_fixtures():
    TEST_PLATES.mkdir(parents=True, exist_ok=True)
    (TEST_PLATES / 'p1.md').write_text(MAINASIDE_MD, encoding='utf-8')
    (TEST_PLATES / 'p2.md').write_text(COLUMNS_MD, encoding='utf-8')


def compile_and_extract() -> tuple:
    """生成 .typ → compile → 返回 (pages, text_p1, text_p2, fills)。"""
    from presswire.render_typst import generate_typ
    text, layouts = generate_typ(str(TEST_PLATES))
    typ_path = REPO_ROOT / f'{OUT_NAME}.typ'
    typ_path.write_text(text, encoding='utf-8')
    pdf_path = typ_path.with_suffix('.pdf')

    r = subprocess.run([TYPST_CLI, 'compile', str(typ_path), str(pdf_path)],
                       capture_output=True, text=True)
    assert r.returncode == 0, f'compile 失败: {r.stderr}'

    from pypdf import PdfReader
    pages = len(PdfReader(str(pdf_path)).pages)

    def page_text(n):
        r = subprocess.run(['pdftotext', '-f', str(n), '-l', str(n), str(pdf_path), '-'],
                           capture_output=True, text=True)
        return r.stdout

    text_p1, text_p2 = page_text(1), page_text(2) if pages >= 2 else ''

    r = subprocess.run([TYPST_CLI, 'eval', 'query(metadata)', '--in', str(typ_path),
                        '--format', 'json'], capture_output=True, text=True)
    fills = {}
    for el in json.loads(r.stdout):
        v = el['value']
        fills[v['plate']] = v['fill']
    return pages, text_p1, text_p2, fills


def cleanup():
    for suffix in ('.typ', '.pdf'):
        p = REPO_ROOT / f'{OUT_NAME}{suffix}'
        if p.exists():
            p.unlink()


def test_mainaside_layout():
    """P1 main-aside: 主栏标题/署名/正文 + 侧栏故事 + 补白 + IN BRIEF。"""
    setup_fixtures()
    try:
        pages, t1, t2, fills = compile_and_extract()
        assert '主栏标题' in t1, '主栏标题缺失'
        assert '记者 张三' in t1, '主栏署名缺失'
        assert '侧栏故事一' in t1, '侧栏故事缺失'
        assert '侧栏故事二' in t1, '侧栏故事二缺失'
        assert '主栏补白' in t1, 'mainbriefs 补白缺失'
        assert 'IN BRIEF' in t1, 'IN BRIEF 缺失'
        assert fills.get('plate-P1', 1.0) < 1.0, 'P1 不应严重溢出'
    finally:
        cleanup()


def test_columns_layout():
    """P2 columns: 等宽 3 栏标题/引文/栏内副故事/IN BRIEF 两组。"""
    setup_fixtures()
    try:
        pages, t1, t2, fills = compile_and_extract()
        assert '等宽多栏版测试标题' in t2, 'columns 标题缺失'
        assert '引文内容测试' in t2, '引文缺失'
        assert '栏内副故事' in t2, '栏内副故事缺失'
        assert t2.count('IN BRIEF') >= 2, f'4 条简讯应分 2 组 IN BRIEF: {t2.count("IN BRIEF")}'
        assert '简讯丁' in t2, '第 4 条简讯缺失（slice 边界）'
        assert fills.get('plate-P2', 1.0) < 1.0, 'P2 不应严重溢出'
    finally:
        cleanup()


def test_pagination_no_trailing_blank():
    """2 版 → 2 页（无尾随空页，2026-08-08 修复）。"""
    setup_fixtures()
    try:
        pages, _, _, _ = compile_and_extract()
        assert pages == 2, f'应 2 页，实际 {pages}'
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
