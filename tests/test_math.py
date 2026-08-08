#!/usr/bin/env python3
"""test_math — 数学公式（任务 11 验收）

验收标准:
    - $...$ inline / block 公式编译通过。
    - 公式字号锁定: show-set 免疫 autofit 字号缩放（expH2/H5 实测——
      内层 text(size:) 对公式无效，必须 show-set）。
    - 公式 CJK 间距: cjk-spacer 依赖（U3 固定字号）。
    - 公式与正文行高共存不溢出固定盒。

说明: 本文件是独立单元测试入口（python3 tests/xxx.py 或 pytest 收集），
任务 19 时统一并入 tests/run_tests.py（docs/plan-revisions.md 第九节第 5 条）。
"""
import sys

SKIP_REASON = '任务 11 未实现——骨架占位'


def main() -> int:
    print(f'[SKIP] {SKIP_REASON}')
    return 0


def test_pending():
    """占位测试：任务实现后替换为真实断言（验收标准见模块 docstring）。"""
    import pytest
    pytest.skip(SKIP_REASON)


if __name__ == '__main__':
    sys.exit(main())
