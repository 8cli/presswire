"""library.py — presswire 库模式门面（2026-08-08 expS 实证，内存通讯）

imposer 内存闭环单一入口: render() → 结构化 dict。
- 控制面进程内: 无 subprocess / 无日志正则；TypstError 异常化（D4 红线
  try/except 优于 panic 退出码 + stderr 正则）
- 数据面留盘: out.pdf / layout.json / demand.json 照写（审计足迹不变）

后端双选（expS 三实验全部坐实，见 dev/research/experiments/expS-typstpy-comm/）:
  - typstpy: typst-py 进程内 compile/eval（Python 3.12 + .venv312；
    3.14 无 wheel 时不可用）——panic TypstError.message 与 CLI stderr
    逐字一致（'content does not fit'）；compile/eval 原生支持 root
  - cli: subprocess typst CLI（现有路径，字节兼容兜底）

用法（imposer 内存模式）:
    from presswire.library import render
    result = render(plates_dir, output, docopts='paper=a3,...',
                    root='~/news', backend='typstpy', write_demand=True)
    fills = result['fills']     # {plate-P1: {fill, deficit_pt, overflow}}
    demand = result['demand']   # 补稿单 dict（None = 已填满）
"""
import json
import os
import subprocess

from . import contracts
from .render_typst import generate_typ

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TYPST_CLI = os.environ.get('TYPST', '/usr/local/bin/typst')
DEFAULT_DOCOPTS = 'paper=a3,landscape,plates=2,columns=3'

ARTICLE_MISMATCH_SIGNAL = 'content does not fit'  # framefit panic（字号固定 100%）
PANIC_SIGNAL = '严重溢出'                          # plate-frame severe-fill panic


# ---------- render-doc 参数序列化（自 cli.py 抽取，双入口共用） ----------

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


def _typstpy_available() -> bool:
    """typst-py 可用性（3.12 venv；3.14 无 wheel 时 import 失败）。"""
    try:
        import typst  # noqa: F401
        return True
    except ImportError:
        return False


def _build_out_typ(plates_dir: str, docopts: str, out_dir: str,
                   autofit: bool, theme: str = '') -> tuple:
    """生成 out.typ 完整文本 + layouts（cli.py 同逻辑抽取）。"""
    if theme and f'theme={theme}' not in docopts:
        docopts = docopts.rstrip(',') + f',theme={theme}'
    opts = contracts.parse_docopts(docopts)
    typ_text, layouts = generate_typ(plates_dir, docopts)
    # 模板路径（相对 out.typ 所在目录）: repo_root/presswire_typst/presswire.typ
    template_abs = os.path.join(REPO_ROOT, 'presswire_typst', 'presswire.typ')
    template_rel = os.path.relpath(template_abs, out_dir).replace(os.sep, '/')
    kw = docopts_to_render(opts)
    kw['autofit'] = autofit
    render_args = render_kw_to_typst(kw)
    typ_text = (
        typ_text.split('#import "presswire_typst/presswire.typ": render-doc')[0]
        + f'#import "{template_rel}": render-doc\n'
        + f'#render-doc(plates, {render_args})\n'
    )
    return typ_text, layouts


# ---------- 后端实现 ----------

def _render_cli(typ_path: str, pdf_path: str, root: str) -> tuple:
    """subprocess typst CLI（现有路径）→ (code, fills, mismatch, panic, stdout, stderr)。"""
    r = subprocess.run([TYPST_CLI, 'compile', '--root', root, typ_path, pdf_path],
                       capture_output=True, text=True)
    code = r.returncode
    mismatch = ARTICLE_MISMATCH_SIGNAL in r.stderr
    panic = f'panicked with: {PANIC_SIGNAL}' in r.stderr
    fills = {}
    if code == 0:
        from .overflow import read_fills
        fills = read_fills(typ_path, root)
    return code, fills, mismatch, panic, r.stdout, r.stderr


def _render_typstpy(typ_path: str, pdf_path: str, root: str) -> tuple:
    """typst-py 进程内 → (code, fills, mismatch, panic, stdout, stderr)。

    D4 红线升级: TypstError 异常化（expS 实验 1: message 与 CLI stderr
    逐字一致）。fills 走进程内 eval（expS 实验 2: root 参数原生支持）。
    """
    import typst
    out_s, err_s = '', ''
    code, mismatch, panic = 0, False, False
    try:
        typst.compile(typ_path, output=pdf_path, root=root)
    except typst.TypstError as e:
        msg = str(e)
        err_s = msg
        code = 1
        if ARTICLE_MISMATCH_SIGNAL in msg:
            mismatch = True
        elif f'panicked with: {PANIC_SIGNAL}' in msg:
            panic = True
        return code, {}, mismatch, panic, out_s, err_s
    # fills: 进程内 eval query(metadata)（等价 CLI --in + --format json）
    try:
        r = typst.eval(typ_path, 'query(metadata)', format='json', root=root)
        from .overflow import parse_fills
        fills = parse_fills(json.loads(r))
    except Exception as e:
        err_s = f'eval query(metadata) 失败: {e}'
        fills = {}
    return code, fills, mismatch, panic, out_s, err_s


# ---------- 门面 ----------

def render(plates_dir: str, output: str,
           docopts: str = DEFAULT_DOCOPTS, theme: str = '',
           autofit: bool = True, root: str | None = None,
           backend: str = 'auto', write_demand: bool = False,
           write_layout: bool = True) -> dict:
    """完整排版闭环 → 结构化 dict（fills/demand/layout/error）。

    `backend`: auto（typst-py 可用则用，否则 cli）| typstpy | cli。
    `write_demand`: True → demand.json 写盘（无需求清空旧单，血泪 #53）。
    返回含 code（0 成功 / 1 编译失败 / 2 参数错误），调用方按 code 处理。
    """
    root = os.path.abspath(root or REPO_ROOT)
    output = os.path.abspath(output)
    result = {
        'ok': False, 'code': 0, 'backend': '', 'engine': 'presswire',
        'out_dir': '', 'pdf': '', 'typ': '',
        'layouts': {}, 'layout_json': {},
        'fills': {}, 'demand': None, 'demand_path': None, 'layout_path': None,
        'article_mismatch': False, 'panic': False,
        'error': None, 'audit_stdout': '', 'audit_stderr': '',
    }
    # --- 沙箱校验（Typst 沙箱: out.typ 与模板资产须在同一 root 内）---
    if not output.startswith(root + os.sep):
        result['error'] = f'❌ output 必须在项目根内（--root {root}）: {output}'
        result['code'] = 2
        return result
    if not os.path.join(REPO_ROOT, 'presswire_typst').startswith(root + os.sep):
        result['error'] = f'❌ --root 必须包含模板资产（presswire_typst/ 在 {REPO_ROOT} 内）'
        result['code'] = 2
        return result

    out_dir = os.path.dirname(output)
    os.makedirs(out_dir, exist_ok=True)
    stem = os.path.splitext(os.path.basename(output))[0]
    typ_path = os.path.join(out_dir, f'{stem}.typ')
    pdf_path = os.path.join(out_dir, f'{stem}.pdf')

    # --- 生成 out.typ ---
    typ_text, layouts = _build_out_typ(plates_dir, docopts, out_dir, autofit, theme)
    with open(typ_path, 'w', encoding='utf-8') as f:
        f.write(typ_text)
    result['out_dir'] = out_dir
    result['typ'] = typ_path
    result['pdf'] = pdf_path
    result['layouts'] = layouts

    # --- 编译 + fills（后端分派）---
    if backend == 'auto':
        backend = 'typstpy' if _typstpy_available() else 'cli'
    if backend == 'typstpy':
        code, fills, mismatch, panic, out_s, err_s = _render_typstpy(typ_path, pdf_path, root)
    else:
        backend = 'cli'
        code, fills, mismatch, panic, out_s, err_s = _render_cli(typ_path, pdf_path, root)
    result['backend'] = backend
    result['code'] = code
    result['fills'] = fills
    # 2026-08-08 信号语义（分栏修复 + fit-copy 废弃）: autofit 模式 severe-fill=1.0
    # 的 panic（"严重溢出"）即"内容超出版心"→ 归并为文章不符合信号；
    # no-autofit 模式 severe-fill=1.05 的 panic 才是真正的严重溢出。
    if autofit and panic:
        panic = False
        mismatch = True
    result['article_mismatch'] = mismatch
    result['panic'] = panic
    result['audit_stdout'] = out_s
    result['audit_stderr'] = err_s
    if code != 0:
        if mismatch:
            result['error'] = ('❌ 内容超出版心（字号固定 100% 适宜阅读，不缩放）: 文章不符合。\n'
                               '   imposer 响应: 选合适长度文章（原文直用）；无合适 → 改写缩小。')
        elif panic:
            result['error'] = f'❌ 严重溢出: typst panic（fill > 1.05）'
        else:
            result['error'] = f'❌ typst compile 失败（退出码 {code}）'
        return result

    # --- layout.json / demand.json（数据面留盘，控制面已进内存）---
    if write_layout:
        result['layout_path'] = contracts.write_layout_json(out_dir, layouts, docopts)
    result['layout_json'] = contracts.layout_json(layouts, docopts)
    from .overflow import plates_fill_demand
    plates_fill = plates_fill_demand(fills)
    result['demand'] = contracts.build_demand(plates_fill)
    if write_demand:
        dpath = contracts.write_demand_json(out_dir, plates_fill)
        stale = os.path.join(out_dir, 'demand.json')
        if dpath:
            result['demand_path'] = dpath
        elif os.path.exists(stale):
            os.remove(stale)
    result['ok'] = True
    return result


if __name__ == '__main__':
    # 自测: 最小 plates → render 全闭环（backend auto 探测）
    import sys
    import tempfile
    import pathlib
    with tempfile.TemporaryDirectory() as td:
        pathlib.Path(td, 'p1.md').write_text(
            'HEADLINE: 测试标题\nBODY:\n第一段。\n\n第二段 **加粗** 与 *斜体*。\n',
            encoding='utf-8')
        res = render(td, os.path.join(td, 'out.pdf'), write_demand=True)
        print(f'backend={res["backend"]} ok={res["ok"]} code={res["code"]}')
        print(f'fills={res["fills"]}')
        print(f'demand={res["demand"]}')
        print(f'pdf 存在: {os.path.exists(res["pdf"])}, demand_path={res["demand_path"]}')
        sys.exit(0 if res['ok'] else 1)
