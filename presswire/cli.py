"""presswire 命令行入口（任务 16 完整接入 + 2026-08-08 库模式门面化）

参数名与 /home/yupeng/news/latex/build.py 保持一致（D2 契约面）:
    presswire <plates_dir> <output.pdf> [--docopts ...] [--theme ...]
              [--no-autofit] [--visual] [--demand] [--pixelcheck PATH]
              [--json] [--backend cli|typstpy|auto]

2026-08-08 重构（内存通讯第 1+3 步）:
  - 流水线主体移入 library.render()（控制面进内存，数据面留盘）
  - cli.main 委托 library → 打印人类可读输出（D2 格式不变）
  - --json: 纯机器模式——stdout 只输出结构化 JSON（imposer 免正则），
    人类行全部转 stderr
  - --backend: cli（subprocess，默认，行为零变化）| typstpy（进程内）| auto

--visual/pixelcheck（任务 18 接入，当前占位提示）。
"""
import argparse
import json
import os
import sys

from .library import render

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def parse_args(argv=None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="presswire: plates/*.md → typst → PDF 报纸生成流水线",
    )
    ap.add_argument("plates_dir", help="plates/ 目录")
    ap.add_argument("output", help="输出 .pdf 路径")
    ap.add_argument(
        "--docopts",
        default="paper=a3,landscape,plates=2,columns=3",
        help="typst 版式选项（逗号分隔）",
    )
    ap.add_argument(
        "--theme",
        default="",
        help="主题: newspaper|magazine|brief（追加到 docopts）",
    )
    ap.add_argument(
        "--no-autofit",
        action="store_true",
        help="关闭自动版面调整（单编译纯生成）",
    )
    ap.add_argument(
        "--visual",
        action="store_true",
        help="视觉验收闭环: 渲染 PDF → 诊断列空白（任务 18 接入）",
    )
    ap.add_argument(
        "--pixelcheck",
        default="",
        help="pixelcheck.py 路径（--visual 时；默认自动探测）",
    )
    ap.add_argument(
        "--demand",
        action="store_true",
        help="autofit 收敛后输出 demand.json（imposer 按单补稿）",
    )
    ap.add_argument(
        "--root",
        default=REPO_ROOT,
        help="Typst 项目根（默认仓库根；日报场景 output 在 ~/news/daily/ 下时指 ~/news/）",
    )
    ap.add_argument(
        "--json",
        action="store_true",
        help="机器模式: stdout 只输出结构化 JSON（fills/demand/layout/error）",
    )
    ap.add_argument(
        "--backend",
        default="cli",
        choices=["cli", "typstpy", "auto"],
        help="排版后端: cli=subprocess typst CLI（默认）| typstpy=进程内 | auto=探测",
    )
    return ap.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    result = render(
        plates_dir=args.plates_dir, output=args.output, docopts=args.docopts,
        theme=args.theme, autofit=not args.no_autofit, root=args.root,
        backend=args.backend, write_demand=args.demand,
    )

    # 机器模式: stdout 纯净 JSON（含错误信号，机器消费者可读 article_mismatch）
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return result['code']

    # 错误: 原始 stderr（如有）+ 格式化错误（与旧 cli 输出一致）
    if result['code'] != 0:
        if result['audit_stderr'] and not result['article_mismatch']:
            print(result['audit_stderr'], file=sys.stderr)
        if result['error']:
            print(result['error'], file=sys.stderr)
        if result['code'] == 1:
            print(f'❌ typst compile 失败（退出码 {result["code"]}）')
        return result['code']

    # fill 报告（stdout 与 latin 同级信息）
    for pid, f in sorted(result['fills'].items()):
        flag = '溢出' if f['overflow'] else ('太空' if f['fill'] < 0.95 else '达标')
        print(f'  {pid}: fill {f["fill"]:.3f} ({flag})')
    print(f'✅ 已生成 {result["pdf"]}（{len(result["layouts"])} 版）')

    # demand 输出（无需求清空旧单，血泪 #53）
    if args.demand:
        if result['demand_path']:
            print(f'  📋 demand.json 已输出: {result["demand_path"]}（imposer 按单补稿）')
        else:
            print('  📋 demand.json: 无需求（版面全部达标，旧补稿单已清空）')

    # --visual 占位（任务 18 接入 pixelcheck）
    if args.visual:
        print('  ⚠️ --visual/pixelcheck 由任务 18 接入（当前仅生成 layout.json）')
    return 0


if __name__ == '__main__':
    sys.exit(main())
