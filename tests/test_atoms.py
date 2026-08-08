#!/usr/bin/env python3
"""test_atoms — atoms.typ 原子组件（任务 9 验收）

验收标准:
    - kicker / headline / deck / byline / dateline / rule / photo 等原子
      输出与 docs/contracts.md 冻结签名一致（含可选字段缺省行为）。
    - 字号随 bodyfontsize 等比缩放（autofit 旋钮语义，linotype
      \bodyfontsize 行为）。
    - 版本日期线 dateline 高度计入版心预算（linotype test_dateline
      防回归: 日期线不挤压主条）。

说明: 本文件是独立单元测试入口（python3 tests/xxx.py 或 pytest 收集），
任务 19 时统一并入 tests/run_tests.py（docs/plan-revisions.md 第九节第 5 条）。
"""
import sys

SKIP_REASON = '任务 9 未实现——骨架占位'


def main() -> int:
    print(f'[SKIP] {SKIP_REASON}')
    return 0


def test_pending():
    """占位测试：任务实现后替换为真实断言（验收标准见模块 docstring）。"""
    import pytest
    pytest.skip(SKIP_REASON)


if __name__ == '__main__':
    sys.exit(main())
