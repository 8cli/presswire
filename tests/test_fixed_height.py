#!/usr/bin/env python3
"""test_fixed_height — 固定版心不推页（任务 7 验收）

验收标准:
    - 内容装入固定盒: 高度 ≤ 帧高时正常排入，页码不推挤（版不推页）。
    - 溢出时报 `Overfull plate: content Xpt > contentH Ypt`（>5% 截断
      才算严重溢出——与 parse_feedback/autofit 同语义）。
    - metadata 写 fill / deficit（任务 17 的输入）。

说明: 本文件是独立单元测试入口（python3 tests/xxx.py 或 pytest 收集），
任务 19 时统一并入 tests/run_tests.py（docs/plan-revisions.md 第九节第 5 条）。
"""
import sys

SKIP_REASON = '任务 7 未实现——骨架占位'


def main() -> int:
    print(f'[SKIP] {SKIP_REASON}')
    return 0


def test_pending():
    """占位测试：任务实现后替换为真实断言（验收标准见模块 docstring）。"""
    import pytest
    pytest.skip(SKIP_REASON)


if __name__ == '__main__':
    sys.exit(main())
