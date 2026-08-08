#!/usr/bin/env python3
"""test_poster — 画报布局 LAYOUT: poster（任务 13 验收，L 量级）

验收标准（mini-spike 验收 + U4）:
    - ≥5 图 + ≥3 段文字无重叠装配、全部落在版心内。
    - pixelcheck 无空白带（生产页无空白）。
    - 降级路径: place 贪心失败时纯 grid 手排可用，U4 放宽。

说明: 本文件是独立单元测试入口（python3 tests/xxx.py 或 pytest 收集），
任务 19 时统一并入 tests/run_tests.py（docs/plan-revisions.md 第九节第 5 条）。
"""
import sys

SKIP_REASON = '任务 13 未实现——骨架占位'


def main() -> int:
    print(f'[SKIP] {SKIP_REASON}')
    return 0


def test_pending():
    """占位测试：任务实现后替换为真实断言（验收标准见模块 docstring）。"""
    import pytest
    pytest.skip(SKIP_REASON)


if __name__ == '__main__':
    sys.exit(main())
