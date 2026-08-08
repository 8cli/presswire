#!/usr/bin/env python3
"""test_pdfcheck — PDF 后处理 QA（任务 18 + U7 验收）

验收标准:
    - pypdf: 页数正确 / 字体嵌入（BaseFont ≥ 2 种）/ MediaBox 尺寸。
    - pdftotext 文本存活（日期线场景: 主条被 vsplit 静默丢弃会被抓到）。
    - 溢出 panic 退出码非 0（typst-py 捕获 TypstError → sys.exit(1)）。
    - U7 视觉等价: pixelcheck 0 FAIL（栏间隙 / 底部溢出 / 空白带）。

说明: 本文件是独立单元测试入口（python3 tests/xxx.py 或 pytest 收集），
任务 19 时统一并入 tests/run_tests.py（docs/plan-revisions.md 第九节第 5 条）。
"""
import sys

SKIP_REASON = '任务 18 未实现——骨架占位'


def main() -> int:
    print(f'[SKIP] {SKIP_REASON}')
    return 0


def test_pending():
    """占位测试：任务实现后替换为真实断言（验收标准见模块 docstring）。"""
    import pytest
    pytest.skip(SKIP_REASON)


if __name__ == '__main__':
    sys.exit(main())
