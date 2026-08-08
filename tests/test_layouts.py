#!/usr/bin/env python3
"""test_layouts — 栏布局（任务 8 验收）

验收标准:
    - columns()/grid(repeat(1fr)) 固定块内列分配正确（expL 基线）。
    - main-aside 布局双版 0 Overfull（结构性缺陷回归，linotype
      test_mainaside_structural 语义）。
    - plates=2 → grid(1fr, 栏缝, 1fr) 并排，无空白首页 + 页数正确
      （linotype test_dual_plate 语义）。

说明: 本文件是独立单元测试入口（python3 tests/xxx.py 或 pytest 收集），
任务 19 时统一并入 tests/run_tests.py（docs/plan-revisions.md 第九节第 5 条）。
"""
import sys

SKIP_REASON = '任务 8 未实现——骨架占位'


def main() -> int:
    print(f'[SKIP] {SKIP_REASON}')
    return 0


def test_pending():
    """占位测试：任务实现后替换为真实断言（验收标准见模块 docstring）。"""
    import pytest
    pytest.skip(SKIP_REASON)


if __name__ == '__main__':
    sys.exit(main())
