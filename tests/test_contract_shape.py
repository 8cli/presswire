#!/usr/bin/env python3
"""test_contract_shape — 接口契约冻结（任务 7b + 12 验收）

验收标准:
    - docs/contracts.md 冻结的 4 组签名逐一成立: plate.typ 固定版心函数、
      atoms.typ 原子、demand.json/layout.json 结构、plates 数据形状。
    - 各模块导出的函数/结构与 contracts.md 一致（字段名/类型/顺序）。
    - plates dict 字段集与 latin parse_plate 等价（D2 红线: 不新增不删除），
      动态对照见 tests/utils/test_parse_anchor.py。

说明: 本文件是独立单元测试入口（python3 tests/xxx.py 或 pytest 收集），
任务 19 时统一并入 tests/run_tests.py（docs/plan-revisions.md 第九节第 5 条）。
"""
import sys

SKIP_REASON = '任务 7b/12 未实现——骨架占位'


def main() -> int:
    print(f'[SKIP] {SKIP_REASON}')
    return 0


def test_pending():
    """占位测试：任务实现后替换为真实断言（验收标准见模块 docstring）。"""
    import pytest
    pytest.skip(SKIP_REASON)


if __name__ == '__main__':
    sys.exit(main())
