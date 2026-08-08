#!/usr/bin/env python3
"""test_cli — 命令行契约（任务 16 验收）

验收标准:
    - build.py 参数面与 latin 一致: <plates_dir> <output> + --docopts /
      --theme / --no-autofit / --visual / --demand（README「build.py CLI 参考」）。
    - 退出码约定: 0 = 成功; 1 = 边界失败（autofit 无法收敛）;
      溢出 panic → typst-py 捕获 TypstError → 非 0（D4 红线修正，
      panic 本身 CLI 退出码为 0，必须用绑定层捕获）。
    - --no-autofit 纯生成不编译。

说明: 本文件是独立单元测试入口（python3 tests/xxx.py 或 pytest 收集），
任务 19 时统一并入 tests/run_tests.py（docs/plan-revisions.md 第九节第 5 条）。
"""
import sys

SKIP_REASON = '任务 16 未实现——骨架占位'


def main() -> int:
    print(f'[SKIP] {SKIP_REASON}')
    return 0


def test_pending():
    """占位测试：任务实现后替换为真实断言（验收标准见模块 docstring）。"""
    import pytest
    pytest.skip(SKIP_REASON)


if __name__ == '__main__':
    sys.exit(main())
