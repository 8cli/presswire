#!/usr/bin/env python3
"""test_CJK — 中文排版（任务 14 验收）

验收标准:
    - 中文+英文混排: 正确断行、标点、基线（cjk-latin-spacing 生效）。
    - 混合文本行高 = CJK 高 ×1.1（expA 实测锚点）。
    - 原生方案: font 分字体描述符 covers "latin-in-cjk" 可用；
      ctyp 作 fallback（标点悬挂/压缩无原生支持 → spike 结论为准）。
    - 中文标题/正文混排不溢出固定盒。

说明: 本文件是独立单元测试入口（python3 tests/xxx.py 或 pytest 收集），
任务 19 时统一并入 tests/run_tests.py（docs/plan-revisions.md 第九节第 5 条）。
"""
import sys

SKIP_REASON = '任务 14 未实现——骨架占位'


def main() -> int:
    print(f'[SKIP] {SKIP_REASON}')
    return 0


def test_pending():
    """占位测试：任务实现后替换为真实断言（验收标准见模块 docstring）。"""
    import pytest
    pytest.skip(SKIP_REASON)


if __name__ == '__main__':
    sys.exit(main())
