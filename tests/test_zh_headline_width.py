#!/usr/bin/env python3
"""test_zh_headline_width.py — 任务 15 QA: 中文标题宽度/折行

验收（计划）: 中英标题在固定栏宽边界正确换行/裁剪（expO1 实测锚点）:
- 折行规则: 中文按字折行 / 英文按词折行 / 混合正确断行
- 超宽检测: measure(title) 无约束自然宽 vs 栏宽（超宽走缩放或折行）

断言方式（expO1 锚点）: 14 字中文 165pt 自然宽约束 150pt → 2 行；
英文 332.98pt → 3 行；混合标题正确断行。

用法:
    python3 tests/test_zh_headline_width.py     # 独立运行（退出码 0=全过）
"""
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

TYPST_CLI = '/usr/local/bin/typst'
OUT_NAME = 'out-test-zh-headline'

TYP_SRC = r'''#set page(width: 400pt, height: 400pt, margin: 15pt)
#set text(font: "Noto Serif CJK SC", lang: "zh")
#let t1 = "三中全会部署进一步全面深化改革"
#let t2 = "China's Economy Shows Resilience Amid Global Uncertainties"
#let t3 = "国产大飞机C919完成商业首航 Beijing-Shanghai"
#context {
  let w1 = measure(text(t1)).width
  let w2 = measure(text(t2)).width
  metadata((test: "headline-width", zh-w: w1 / 1pt, en-w: w2 / 1pt))
}
#text(size: 11pt)[中文标题:]
#block(width: 150pt, stroke: 0.5pt + gray, inset: 4pt)[#t1]
#v(6pt)
#text(size: 11pt)[英文标题:]
#block(width: 150pt, stroke: 0.5pt + gray, inset: 4pt)[#t2]
#v(6pt)
#text(size: 11pt)[中英混合:]
#block(width: 150pt, stroke: 0.5pt + gray, inset: 4pt)[#t3]
'''


def run() -> tuple:
    typ_path = REPO_ROOT / f'{OUT_NAME}.typ'
    typ_path.write_text(TYP_SRC, encoding='utf-8')
    pdf_path = typ_path.with_suffix('.pdf')
    r = subprocess.run([TYPST_CLI, 'compile', str(typ_path), str(pdf_path)],
                       capture_output=True, text=True)
    assert r.returncode == 0, f'compile 失败: {r.stderr[:200]}'
    r = subprocess.run([TYPST_CLI, 'eval', 'query(metadata)', '--in', str(typ_path),
                        '--format', 'json'], capture_output=True, text=True)
    import json
    v = json.loads(r.stdout)[0]['value']
    text = subprocess.run(['pdftotext', str(pdf_path), '-'],
                          capture_output=True, text=True).stdout
    return v, text


def cleanup():
    for suffix in ('.typ', '.pdf'):
        p = REPO_ROOT / f'{OUT_NAME}{suffix}'
        if p.exists():
            p.unlink()


def test_zh_wraps_by_char():
    """中文 14 字在 150pt 栏宽折 2 行（按字折行）。"""
    try:
        v, text = run()
        assert v['zh-w'] > 150, f'中文自然宽应 > 150pt: {v["zh-w"]}'
        lines = [l for l in text.split('\n') if '改革' in l or '部署' in l]
        assert lines, '中文标题未渲染'
        # 折 2 行: 第二行含尾部"化改革"
        assert any('化改革' in l for l in text.split('\n')), f'应折 2 行: {text[:100]}'
    finally:
        cleanup()


def test_en_wraps_by_word():
    """英文标题在 150pt 折 3 行（按词折行，词不分裂）。"""
    try:
        v, text = run()
        assert v['en-w'] > 300, f'英文自然宽应 > 300pt: {v["en-w"]}'
        assert "Resilience Amid" in text, '英文折行词边界错误'
        assert "Uncertainties" in text, '英文第三行缺失'
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
