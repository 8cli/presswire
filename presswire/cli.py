"""presswire 命令行入口（任务 16 完整接入）

参数名与 /home/yupeng/news/latex/build.py 保持一致（D2 契约面）:
    presswire <plates_dir> <output.pdf> [--docopts ...] [--theme ...]
              [--no-autofit] [--visual] [--demand] [--pixelcheck PATH]

流程（对应 latin build.py main）:
    1. 解析 docopts（contracts.parse_docopts）→ render-doc 参数映射
    2. generate_typ → out.typ（与 output 同目录，模板相对路径）
    3. typst compile → output.pdf
    4. 写 layout.json（contracts.layout_json）
    5. --demand: eval 'query(metadata)' → fill → demand.json（无需求清旧单）
    6. stdout 与 latin 同级信息（PDF/版数/fill 报告）

--visual/pixelcheck（任务 18 接入，当前占位提示）。
"""
import argparse
import json
import os
import subprocess
import sys

from . import contracts
from .render_typst import generate_typ

TYPST_CLI = os.environ.get('TYPST', '/usr/local/bin/typst')
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
    return ap.parse_args(argv)


def docopts_to_render(docopts: dict) -> dict:
    """docopts → render-doc 命名参数（paper 尺寸/margin/plates-per-page/theme）。"""
    kw = {}
    paper = docopts.get('paper', 'a3')
    landscape = docopts.get('landscape', False) is True or docopts.get('landscape') == 'true'
    if paper == 'a3':
        kw['paper-width'], kw['paper-height'] = ('420mm', '297mm') if landscape else ('297mm', '420mm')
    elif paper == 'a4':
        kw['paper-width'], kw['paper-height'] = ('297mm', '210mm') if landscape else ('210mm', '297mm')
    elif paper == 'letter':
        kw['paper-width'], kw['paper-height'] = ('279mm', '216mm') if landscape else ('216mm', '279mm')
    kw['plates-per-page'] = int(docopts.get('plates', '1'))
    if docopts.get('theme'):
        kw['theme'] = str(docopts['theme'])
    return kw


def render_kw_to_typst(kw: dict) -> str:
    """render-doc 命名参数 dict → Typst 调用参数串。

    值类型保持: 数字不带引号（plates-per-page: 2）、bool 小写、
    length 原样（420mm）、其余字符串带引号。
    """
    parts = []
    for k, v in kw.items():
        if isinstance(v, bool):
            parts.append(f'{k}: {str(v).lower()}')
        elif isinstance(v, (int, float)):
            parts.append(f'{k}: {v}')
        elif k in ('paper-width', 'paper-height'):
            parts.append(f'{k}: {v}')
        else:
            parts.append(f'{k}: "{v}"')
    return ', '.join(parts)


def compile_typ(typ_path: str, pdf_path: str) -> int:
    """typst compile → 返回退出码（panic 退出码 1，D4 红线实证）。

    --root REPO_ROOT: out.typ 在子目录（如 examples/）时模板 ../ 上溯在 root 内；
    图片等资产同理相对 root 解析（任务 10 路径语义）。
    """
    r = subprocess.run([TYPST_CLI, 'compile', '--root', REPO_ROOT, typ_path, pdf_path],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr, file=sys.stderr)
    return r.returncode


def read_fills(typ_path: str) -> dict:
    """eval query(metadata) → {plate: {fill, deficit_pt, overflow}}（任务 17 overflow.py）。"""
    from .overflow import read_fills as _read
    return _read(typ_path, REPO_ROOT)


def main(argv=None) -> int:
    args = parse_args(argv)
    if args.theme and f'theme={args.theme}' not in args.docopts:
        args.docopts = args.docopts.rstrip(',') + f',theme={args.theme}'
    opts = contracts.parse_docopts(args.docopts)

    # 1. 生成 .typ（与 output 同目录，模板相对路径）
    output = os.path.abspath(args.output)
    # Typst 沙箱: out.typ 与模板资产（presswire_typst/）须在同一 root 内
    # （同 latin "cwd = 引擎目录"先例——模板类文件须可访问）
    if not output.startswith(REPO_ROOT + os.sep):
        print(f'❌ output 必须在仓库根内（模板资产访问）: {REPO_ROOT}', file=sys.stderr)
        return 2
    out_dir = os.path.dirname(output)
    os.makedirs(out_dir, exist_ok=True)
    stem = os.path.splitext(os.path.basename(output))[0]
    typ_path = os.path.join(out_dir, f'{stem}.typ')

    typ_text, layouts = generate_typ(args.plates_dir, args.docopts)
    # 模板路径（相对 out.typ 所在目录）: repo_root/presswire_typst/presswire.typ
    template_abs = os.path.join(REPO_ROOT, 'presswire_typst', 'presswire.typ')
    template_rel = os.path.relpath(template_abs, out_dir).replace(os.sep, '/')
    kw = docopts_to_render(opts)
    kw['autofit'] = not args.no_autofit
    render_args = render_kw_to_typst(kw)
    typ_text = (
        typ_text.split('#import "presswire_typst/presswire.typ": render-doc')[0]
        + f'#import "{template_rel}": render-doc\n'
        + f'#render-doc(plates, {render_args})\n'
    )
    with open(typ_path, 'w', encoding='utf-8') as f:
        f.write(typ_text)

    # 2. 编译
    pdf_path = os.path.join(out_dir, f'{stem}.pdf')
    code = compile_typ(typ_path, pdf_path)
    if code != 0:
        print(f'❌ typst compile 失败（退出码 {code}）')
        return code

    # 3. layout.json
    layout_path = contracts.write_layout_json(out_dir, layouts, args.docopts)

    # 4. fill 报告（stdout 与 latin 同级信息）
    fills = read_fills(typ_path)
    if fills:
        for pid, f in sorted(fills.items()):
            flag = '溢出' if f['overflow'] else ('太空' if f['fill'] < 0.95 else '达标')
            print(f'  {pid}: fill {f["fill"]:.3f} ({flag})')
    print(f'✅ 已生成 {pdf_path}（{len(layouts)} 版）')

    # 5. --demand: demand.json（无需求清空旧单，血泪 #53）
    if args.demand:
        from .overflow import plates_fill_demand
        plates_fill = plates_fill_demand(fills)
        dpath = contracts.write_demand_json(out_dir, plates_fill)
        stale = os.path.join(out_dir, 'demand.json')
        if dpath:
            print(f'  📋 demand.json 已输出: {dpath}（imposer 按单补稿）')
        else:
            if os.path.exists(stale):
                os.remove(stale)
            print('  📋 demand.json: 无需求（版面全部达标，旧补稿单已清空）')

    # 6. --visual 占位（任务 18 接入 pixelcheck）
    if args.visual:
        print('  ⚠️ --visual/pixelcheck 由任务 18 接入（当前仅生成 layout.json）')
    return 0


if __name__ == '__main__':
    sys.exit(main())
