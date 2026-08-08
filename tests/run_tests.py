#!/usr/bin/env python3
"""presswire 回归测试 runner — 骨架（任务 19/20 前置）。

用法:
    python3 tests/run_tests.py              # 发现并运行 tests/ 下 test_*.py

设计（承接 linotype tests/run_tests.py 约定）:
    linotype runner = 14 个 test_* 函数 + report() 打点 + 退出码 0/1
    （参考: /home/yupeng/news/latex/tests/run_tests.py）。
    本骨架把「每个 test_* 块」物化为「独立测试文件」: 每个文件独立可跑
    （python3 tests/xxx.py），也可被本 runner 聚合。文件级状态判定:

        exit 0 且输出含 "[SKIP]" 行  → SKIP（占位 / 环境缺失，不算失败）
        exit 0                       → PASS
        其他                         → FAIL（traceback / 退出码非 0）

    幂等: 清单（MANIFEST）中缺失的文件只记 ⚠ MISSING 提示，不失败；
          重复运行结果一致；单个文件崩溃不影响其他文件。

    退出码: 0 = 无 FAIL; 1 = 有 FAIL（SKIP / MISSING 不计失败）。

与任务 19 的衔接（docs/plan-revisions.md 第九节第 5 条）:
    任务 19 把 linotype 的 14 个测试函数迁入本文件（+ report() 聚合），
    独立文件保留为单元测试入口。本文件已预留 typst_available() 供迁移
    使用——依赖 typst 的用例在无 wheel 环境（本机 Python 3.14 即如此）
    应 try/except ImportError 跳过或标 [SKIP]，不报错。
"""
import ast
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TESTS_DIR = REPO_ROOT / 'tests'

# 期望存在的独立测试文件（相对 tests/）。缺失仅提示，不失败——任务
# 实现者创建占位后即自动被 discovery 拾取，无需改本文件。
MANIFEST: list[str] = [
    'test_contract_shape.py',
    'test_fixed_height.py',
    'test_layouts.py',
    'test_theme.py',
    'test_atoms.py',
    'test_autofit.py',
    'test_math.py',
    'test_poster.py',
    'test_CJK.py',
    'test_zh_headline_width.py',
    'test_cli.py',
    'test_demand.py',
    'test_pdfcheck.py',
    'utils/test_parse_anchor.py',
]

SKIP_RE = re.compile(r'^\[SKIP\]', re.MULTILINE)
TIMEOUT = 600  # 秒/文件（typst 编译类测试放宽）


def typst_available() -> bool:
    """typst-py 是否可用（进程内编译路径）。Python 3.14 无 wheel → False。"""
    try:
        import typst  # noqa: F401
        return True
    except ImportError:
        return False


def discover() -> list[Path]:
    """递归发现 tests/ 下 test_*.py（排除 runner 自身）。"""
    return sorted(
        p for p in TESTS_DIR.glob('**/test_*.py') if p.name != 'run_tests.py'
    )


def file_description(path: Path) -> str:
    """模块 docstring 首行（测试文件自述）。"""
    try:
        doc = ast.get_docstring(ast.parse(path.read_text(encoding='utf-8')))
    except Exception:
        return ''
    if doc:
        return doc.strip().splitlines()[0].strip('. :')
    return ''


def run_file(path: Path) -> tuple[str, str]:
    """子进程运行单个测试文件 → (状态, 原始输出)。"""
    rel = path.relative_to(TESTS_DIR).as_posix()
    try:
        r = subprocess.run(
            [sys.executable, str(path)], cwd=REPO_ROOT,
            capture_output=True, text=True, timeout=TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return 'FAIL', f'{rel}: 超时（>{TIMEOUT}s）'
    out = ((r.stdout or '') + (r.stderr or '')).strip()
    if r.returncode == 0:
        state = 'SKIP' if SKIP_RE.search(out) else 'PASS'
    else:
        state = 'FAIL'
    return state, out


def _detail_tail(out: str, max_lines: int = 3) -> str:
    """输出摘要: 末尾非空行（FAIL 多给几行看 traceback）。"""
    lines = [ln for ln in out.splitlines() if ln.strip()]
    return '\n        '.join(lines[-max_lines:]) if lines else ''


def main() -> int:
    print('=== presswire 回归测试 ===')
    print(f'tests 目录: {TESTS_DIR}')
    print('typst-py: ' + ('可用（进程内编译路径）' if typst_available()
                          else '不可用（3.14 无 wheel → 依赖 typst 的测试将 SKIP）'))

    discovered = discover()
    existing = {p.relative_to(TESTS_DIR).as_posix() for p in discovered}
    counts = {'PASS': 0, 'SKIP': 0, 'FAIL': 0, 'MISSING': 0}

    print(f'\n发现 {len(discovered)} 个测试文件（清单 {len(MANIFEST)} 项）:')
    for name in MANIFEST:  # 幂等: 缺失项仅提示，不失败
        if name not in existing:
            counts['MISSING'] += 1
            print(f'  ⚠ MISSING {name}（未创建，忽略）')

    for path in discovered:
        rel = path.relative_to(TESTS_DIR).as_posix()
        state, out = run_file(path)
        counts[state] += 1
        tag = {'PASS': '✅ PASS', 'SKIP': '⏭ SKIP', 'FAIL': '❌ FAIL'}[state]
        desc = file_description(path)
        print(f'\n  {tag} {rel}' + (f' — {desc}' if desc else ''))
        if out:
            print(f'        {_detail_tail(out, 5 if state == "FAIL" else 3)}')

    total = counts['PASS'] + counts['SKIP'] + counts['FAIL']
    print(f'\n{counts["PASS"]} PASS, {counts["SKIP"]} SKIP, '
          f'{counts["FAIL"]} FAIL'
          + (f', {counts["MISSING"]} MISSING(清单)' if counts['MISSING'] else ''))
    verdict = '✅ 全部通过（含 SKIP）' if counts['FAIL'] == 0 else '❌ 有失败'
    print(f'结果: {verdict}（{total} 文件）')
    return 1 if counts['FAIL'] else 0


if __name__ == '__main__':
    sys.exit(main())
