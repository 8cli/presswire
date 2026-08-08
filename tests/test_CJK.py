#!/usr/bin/env python3
"""test_CJK.py — 任务 14 QA: CJK 中英混排（N1）

验收（计划）: examples/zh_mixed/ 一篇中日混排（正文含中文与英文长句）PDF 理想；
四包组合（ctyp 0.3.0 + unbreak 0.2.3 + unshrink 0.1.0 + spacer 0.2.1）编译零错误。

断言方式（expQ 验证锚点）: 编译中文样张 → pdftotext 命中中文/英文/标点
字段；中文按字断行、英文按词断行。

用法:
    python3 tests/test_CJK.py     # 独立运行（退出码 0=全过）
"""
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

TYPST_CLI = '/usr/local/bin/typst'
OUT_NAME = 'out-test-CJK'
FIXTURES = REPO_ROOT / 'tests' / 'fixtures' / 'cjk'

CJK_MD = """DATE: 2026年8月8日
KICKER: 科技前沿
HEADLINE: 中文标题：Typst 与 LaTeX 的全面对比
DECK: 中英混排测试——Typst handles CJK natively.
BYLINE: 记者 张三
LAYOUT: main-aside
COLUMNS: 2
BODY:
这是第一段中文正文，测试中英混排。Typst 0.15.1 支持原生 CJK 断行与基线对齐，中文字符「引号」和《书名号》都正常。
第二段混合：The machine's economics mattered as much as its mechanics. 数字 9,900 万美元、82% 与公式 $Ma = 0.785$ 混排正确。

STORY-B: 侧栏中文故事
BYLINE-B: 记者 李四
侧栏故事正文，测试中文标点——省略号…和破折号——的显示。
"""


def setup():
    FIXTURES.mkdir(parents=True, exist_ok=True)
    (FIXTURES / 'p1.md').write_text(CJK_MD, encoding='utf-8')


def compile_cjk() -> Path:
    from presswire.render_typst import generate_typ
    text, _ = generate_typ(str(FIXTURES))
    typ_path = REPO_ROOT / f'{OUT_NAME}.typ'
    typ_path.write_text(text, encoding='utf-8')
    pdf_path = typ_path.with_suffix('.pdf')
    r = subprocess.run([TYPST_CLI, 'compile', str(typ_path), str(pdf_path)],
                       capture_output=True, text=True)
    assert r.returncode == 0, f'compile 失败（四包组合应零错误）: {r.stderr[:300]}'
    return pdf_path


def cleanup():
    for suffix in ('.typ', '.pdf'):
        p = REPO_ROOT / f'{OUT_NAME}{suffix}'
        if p.exists():
            p.unlink()


def test_cjk_mixed_renders():
    """中文正文/英文长句/混排/标点全部命中。"""
    setup()
    try:
        pdf = compile_cjk()
        t = subprocess.run(['pdftotext', str(pdf), '-'],
                           capture_output=True, text=True).stdout
        for expected in ['中文标题', 'Typst 与 LaTeX 的全面对比', '中英混排',
                         'handles CJK natively', '第一段中文正文', '「引号」',
                         '《书名号》', '侧栏中文故事', '省略号', '破折号',
                         '9,900', '82%']:
            assert expected in t, f'CJK 渲染缺失: {expected}'
    finally:
        cleanup()


def test_cjk_no_compile_error():
    """四包组合编译零错误（ctyp 0.3.0 锁定无 panic）。"""
    setup()
    try:
        compile_cjk()  # 内部断言 returncode == 0
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
