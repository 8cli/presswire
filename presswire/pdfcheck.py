#!/usr/bin/env python3
"""pdfcheck.py — presswire PDF 后处理检查（移植 latin pdfcheck.py，任务 18）

检查项（适配 Typst 语义）:
  1. PANIC: 编译日志含 panicked → FAIL（严重溢出/语法错误，D4 红线）
  2. MEDIA BOX: PDF 页尺寸匹配期望纸张（A3 420×297 / A4 210×297 / Letter 279×216）
  3. FONTS: 嵌入字体 ≥2 种（Regular + Bold，防回退系统字体）
  4. PAGES: 页数匹配预期（单版 N 页 / 双版 ceil(N/2) 页）

用法:
    python3 pdfcheck.py <pdf路径> [--log <编译日志>] [--paper a3|a4|letter]
                       [--landscape] [--pages N]

退出码: 0 = 全部通过; 1 = 有 FAIL。
"""
import argparse
import re
import sys
from pypdf import PdfReader

# 期望纸张尺寸 (mm)
PAPER_MM = {
    'a3': (297, 420),      # 宽 x 高（竖版基准）
    'a4': (210, 297),
    'letter': (216, 279),
}

PASSED: list[str] = []
FAILED: list[str] = []


def report(name: str, ok: bool, detail: str = '') -> None:
    tag = '✅ PASS' if ok else '❌ FAIL'
    print(f'  {tag} {name}{(" — " + detail) if detail else ""}')
    (PASSED if ok else FAILED).append(name)


def check_log(log_path: str) -> None:
    if not log_path:
        report('LOG', True, '未提供日志，跳过')
        return
    try:
        text = open(log_path, encoding='utf-8', errors='replace').read()
    except FileNotFoundError:
        report('LOG', False, f'日志不存在: {log_path}')
        return
    # 1. panic（presswire 严重溢出 → #panic → typst panicked）
    panics = re.findall(r'panicked with: ([^\n]+)', text)
    if panics:
        report('PANIC', False, f'{len(panics)} 处 panic: {panics[0][:60]}')
    else:
        report('PANIC', True, '无 panic')
    # 2. 其他错误（error: 提示，非 panic）
    errors = re.findall(r'^error: ', text, re.MULTILINE)
    report('LOG ERROR', len(errors) == 0, f'{len(errors)} 个错误' if errors else '无错误')


def check_pdf(pdf_path: str, paper: str, landscape: bool, expect_pages: int) -> None:
    try:
        reader = PdfReader(pdf_path)
    except Exception as e:
        report('PDF', False, f'无法读取: {e}')
        return
    # MEDIA BOX
    page = reader.pages[0]
    mb = page.mediabox
    w_mm = float(mb.width) * 25.4 / 72
    h_mm = float(mb.height) * 25.4 / 72
    expected = PAPER_MM[paper]
    if landscape:
        expected = (expected[1], expected[0])
    ok = abs(w_mm - expected[0]) < 1 and abs(h_mm - expected[1]) < 1
    report('MEDIA BOX', ok, f'{w_mm:.1f}×{h_mm:.1f}mm（期望 {expected[0]}×{expected[1]}mm）')
    # FONTS（pypdf: page['/Resources']['/Font'] 的键是字体资源名）
    fonts = set()
    for pg in reader.pages:
        res = pg.get('/Resources', {})
        fonts.update((res.get('/Font') or {}).keys())
    report('FONTS', len(fonts) >= 2, f'{len(fonts)} 种字体资源' if fonts else '无嵌入字体')
    # PAGES
    n = len(reader.pages)
    report('PAGES', n == expect_pages, f'{n} 页（期望 {expect_pages}）')


def main() -> int:
    ap = argparse.ArgumentParser(description='presswire PDF 检查')
    ap.add_argument('pdf', help='PDF 路径')
    ap.add_argument('--log', default='', help='编译日志路径（typst stderr）')
    ap.add_argument('--paper', default='a3', choices=['a3', 'a4', 'letter'])
    ap.add_argument('--landscape', action='store_true')
    ap.add_argument('--pages', type=int, default=0, help='期望页数（0 = 自动跳过）')
    args = ap.parse_args()

    check_log(args.log)
    check_pdf(args.pdf, args.paper, args.landscape, args.pages)

    total = len(PASSED) + len(FAILED)
    print(f'\n{"✅" if not FAILED else "❌"} {len(PASSED)}/{total} 通过')
    return 0 if not FAILED else 1


if __name__ == '__main__':
    sys.exit(main())
