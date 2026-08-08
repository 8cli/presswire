#!/usr/bin/env python3
"""test_theme — 主题预设（任务 5 空版占位 + 8 主题，验收）

验收标准:
    - broadsheet / magazine 主题编译通过（linotype test_theme 语义）。
    - 主题预设生效: 字体 + 配色（ink / accent / papercolor）按
      --docopts 键注入，magazine 与 broadsheet 产物可区分。

说明: 本文件是独立单元测试入口（python3 tests/xxx.py 或 pytest 收集），
任务 19 时统一并入 tests/run_tests.py（docs/plan-revisions.md 第九节第 5 条）。
"""
import sys

SKIP_REASON = '任务 5/8 主题未实现——骨架占位'


def main() -> int:
    print(f'[SKIP] {SKIP_REASON}')
    return 0


def test_pending():
    """占位测试：任务实现后替换为真实断言（验收标准见模块 docstring）。"""
    import pytest
    pytest.skip(SKIP_REASON)


if __name__ == '__main__':
    sys.exit(main())
