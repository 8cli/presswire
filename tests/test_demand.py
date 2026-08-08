#!/usr/bin/env python3
"""test_demand — demand.json 补白请求（任务 17 验收）

验收标准:
    - measure 对比模式: 无约束 measure(text).width 得自然宽 W；
      约束 measure(width: W₀, text).height 得高 H → W > W₀ 且 H 单行
      判不可断行溢出（双测法防假阴性）。
    - 进程内 typst.eval("out.typ", "query(metadata)") 返回 JSON →
      Python 按 label 分组（含 label 字段，expB 实证）→ fill/deficit。
    - demand.json 结构与 docs/contracts.md 冻结一致。
    - 降级路径: typst-py 不可用时子进程 `typst eval` CLI。

说明: 本文件是独立单元测试入口（python3 tests/xxx.py 或 pytest 收集），
任务 19 时统一并入 tests/run_tests.py（docs/plan-revisions.md 第九节第 5 条）。
"""
import sys

SKIP_REASON = '任务 17 未实现——骨架占位'


def main() -> int:
    print(f'[SKIP] {SKIP_REASON}')
    return 0


def test_pending():
    """占位测试：任务实现后替换为真实断言（验收标准见模块 docstring）。"""
    import pytest
    pytest.skip(SKIP_REASON)


if __name__ == '__main__':
    sys.exit(main())
