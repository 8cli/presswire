"""presswire 命令行入口（argparse 桩，逻辑在任务 16 完整接入）。

参数名与 /home/yupeng/news/latex/build.py 保持一致（契约面）。
"""

import argparse


def main() -> int:
    ap = argparse.ArgumentParser(
        description="presswire: plates/*.md → typst → PDF 报纸生成流水线",
    )
    ap.add_argument("plates_dir", help="plates/ 目录")
    ap.add_argument("output", help="输出路径")
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
        help="关闭自动版面调整",
    )
    ap.add_argument(
        "--visual",
        action="store_true",
        help="视觉验收闭环: 渲染 PDF → 诊断列空白",
    )
    ap.add_argument(
        "--demand",
        action="store_true",
        help="autofit 收敛后输出 demand.json（imposer 按单补稿）",
    )
    ap.parse_args()
    # TODO(任务 16): 完整解析/渲染逻辑
    return 0


if __name__ == "__main__":
    main()
