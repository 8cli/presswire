#!/usr/bin/env python3
"""test_zh_headline_width — 中文标题宽度（任务 15 验收）

验收标准（expO1 实测锚点）:
    - 折行规则: 中文按字折行 / 英文按词折行 / 混合正确断行。
    - 超宽检测: measure(title) 无约束自然宽 vs 栏宽 → 超宽走
      one-liner 缩放或接受折行。
    - 已知锚点: 14 字中文 165pt 自然宽折 2 行；英文 332.98pt 折 3 行。

说明: 本文件是独立单元测试入口（python3 tests/xxx.py 或 pytest 收集），
任务 19 时统一并入 tests/run_tests.py（docs/plan-revisions.md 第九节第 5 条）。
"""
import sys

SKIP_REASON = '任务 15 未实现——骨架占位'


def main() -> int:
    print(f'[SKIP] {SKIP_REASON}')
    return 0


def test_pending():
    """占位测试：任务实现后替换为真实断言（验收标准见模块 docstring）。"""
    import pytest
    pytest.skip(SKIP_REASON)


if __name__ == '__main__':
    sys.exit(main())
