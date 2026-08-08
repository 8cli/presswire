#!/usr/bin/env python3
"""test_autofit — autofit 自动版面（任务 10 + 18 验收）

验收标准（对应 linotype 4 个 autofit 测试函数）:
    - 溢出收敛: 超长内容 → 自动缩字号/增栏数 → 0 Overfull + min fill ≥ 45%。
    - 太空: 极短内容 → 增大字号/减栏数 → fill 提升或边界接受（不崩溃）。
    - 边界: 极长内容 → 到达边界 → 明确失败报告（exit 1 + 最优尝试）。
    - --no-autofit: 纯生成 .typ 不编译（无 .pdf）。

说明: 本文件是独立单元测试入口（python3 tests/xxx.py 或 pytest 收集），
任务 19 时统一并入 tests/run_tests.py（docs/plan-revisions.md 第九节第 5 条）。
"""
import sys

SKIP_REASON = '任务 10/18 未实现——骨架占位'


def main() -> int:
    print(f'[SKIP] {SKIP_REASON}')
    return 0


def test_pending():
    """占位测试：任务实现后替换为真实断言（验收标准见模块 docstring）。"""
    import pytest
    pytest.skip(SKIP_REASON)


if __name__ == '__main__':
    sys.exit(main())
