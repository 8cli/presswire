"""render_typst.py — dict → Typst 数据文本（任务 5）

将 parse_plate 的 dict 转成 Typst 数据字面量 `#let plates = (...)`，
语义保留全部字段（D2 红线: 不新增、不删除字段）。

转义（2026-08-07 expJ 定案）:
 - 正文/标题等纯文本走 **code 字符串路径**: `# $ < > [ ] * _ { }` 全安全，
   仅 `\\` → `\\\\`、`"` → `\\"` 需转义（引号是字符串定界符）——plates.py
   的 `_escape()` 已处理，此处直接套引号。
 - 富文本字段（加粗/公式/图片）的 markup 渲染在后续任务（atoms.typ 任务 10、
   math.typ 任务 12）实现；本任务先以 code 字符串保真输出（不丢内容）。

产出（与 latin build.py generate_tex 对应）:
 - `generate_typ(plates_dir, docopts)` → (typ_text, layouts)
   typ_text: `#let plates = (...)` 数据段 + `#import` 模板 + `#render-doc(plates)`
   layouts:  {p1: 'multi'|'single', ...}（layout.json 消费，contracts 任务 6）
"""
import os
import re

__all__ = ['generate_typ', 'render_plates_data', 'render_plate']

# markdown 标记: **bold** / *italic*（latin 输入风格，_escape 原样保留）
# 公式: $...$（内联紧凑）/ $ ... $（块级带空格，Typst 语法区分）
_MD_MARK_RE = re.compile(r'\$(.+?)\$|\*\*(.+?)\*\*|(?<!\*)\*([^*]+?)\*(?!\*)')


def _typst_str(s: str) -> str:
    """Python 字符串 → Typst code 字符串字面量（值已 _escape，直接加引号）。"""
    return '"' + s + '"'


def _typst_value(s: str) -> str:
    """字符串值 → Typst 字面量。

    纯文本 → code 字符串（免转义路径）；含富文本标记（公式 $...$ /
    markdown **x**/*x*）→ content 表达式（math.equation/strong/emph 函数
    调用——2026-08-08 实测: 字符串插值不解析 markup，须结构化构建 content）。
    模板渲染兼容字符串与 content 两种值类型。
    """
    # 纯公式行（整段 strip 后为 $...$）→ 块级公式标记 dict
    # （2026-08-08 实测: 块级公式在 par 段落内被忽略——模板对 dict 元素
    # 直接渲染 math.equation 不包 par）
    t = s.strip()
    if len(t) > 2 and t.startswith('$') and t.endswith('$'):
        return f'("__block-math__": math.equation({_typst_str(t[1:-1].strip())}, block: true))'
    # 画报 body 图片标记 ![](path)（任务 13 N3）→ __poster-img__ dict；
    # latin 无此标记（body 内 ![]() 为字面文本），presswire 新能力
    img_m = re.match(r'^!\[\]\((.+?)\)$', t)
    if img_m:
        return f'("__poster-img__": {_typst_str(img_m.group(1))})'
    if not _MD_MARK_RE.search(s):
        return _typst_str(s)
    parts = []
    pos = 0
    for m in _MD_MARK_RE.finditer(s):
        if m.start() > pos:
            parts.append(_typst_str(s[pos:m.start()]))
        if m.group(1) is not None:
            # 公式: $...$ 紧凑 → 内联（block: false）；$ ... $ 带首尾空格 → 块级
            body = m.group(1)
            block = body != body.strip() or body.strip() == ''
            parts.append(f'math.equation({_typst_str(body.strip())}, block: {str(block).lower()})')
        elif m.group(2) is not None:
            parts.append(f'strong({_typst_str(m.group(2))})')
        else:
            parts.append(f'emph({_typst_str(m.group(3))})')
        pos = m.end()
    if pos < len(s):
        parts.append(_typst_str(s[pos:]))
    if len(parts) == 1:
        return parts[0]
    return '(' + ' + '.join(parts) + ')'


def _typst_array(items: list) -> str:
    """Typst 数组字面量。

    **单元素陷阱**（2026-08-08 实测）: `(x)` 在 Typst 是括号分组（= x 本身），
    必须 `(x,)` 尾逗号才是数组。空数组 → `()`。
    """
    if not items:
        return '()'
    return '(' + ', '.join(items) + ',)'


def _typst_plates_list(v: list) -> str:
    """字符串数组 → Typst 数组字面量（富文本标记转 content 表达式）。"""
    return _typst_array([_typst_value(x) for x in v])


def _typst_story(st: dict) -> str:
    """副故事 dict → Typst 字典字面量（键顺序: headline/byline/body 固定）。"""
    parts = []
    for k in ('headline', 'byline', 'body'):
        val = st.get(k, '')
        if isinstance(val, list):
            parts.append(f'"{k}": {_typst_plates_list(val)}')
        else:
            parts.append(f'"{k}": {_typst_value(val)}')
    return '(' + ', '.join(parts) + ')'


def render_plate(p: dict) -> str:
    """单个版 dict → Typst 字典字面量（字段顺序与 parse_plate 返回一致）。"""
    keys = [
        'kicker', 'headline', 'subheadline', 'deck', 'byline', 'date', 'body',
        'pullquote', 'briefs', 'mainbriefs', 'stories', 'layout', 'columns',
        'expanded', 'image', 'imagewidth', 'imagecaption',
    ]
    parts = []
    for k in keys:
        val = p.get(k, '')
        if isinstance(val, list):
            if k == 'stories':
                parts.append(f'"{k}": {_typst_array([_typst_story(st) for st in val])}')
            else:
                parts.append(f'"{k}": {_typst_plates_list(val)}')
        else:
            parts.append(f'"{k}": {_typst_value(val)}')
    return '(' + ', '.join(parts) + ')'


def render_plates_data(plates: list) -> str:
    """版数组 → `#let plates = (...)` 数据段。空数组 → `#let plates = ()`。"""
    if not plates:
        return '#let plates = ()'
    inner = ',\n  '.join(render_plate(p) for p in plates)
    return '#let plates = (\n  ' + inner + ',\n)'


def _read_plates(plates_dir: str) -> list:
    """读 plates 目录全部 .md → parse_plate dict 数组（文件名排序，同 latin）。"""
    files = sorted(f for f in os.listdir(plates_dir) if f.endswith('.md'))
    if not files:
        raise SystemExit(f'错误: plates 目录 {plates_dir} 无 .md 文件')

    # 延迟 import（plates.py 是本模块同包依赖）
    from .plates import parse_plate
    return [parse_plate(open(os.path.join(plates_dir, f), encoding='utf-8').read())
            for f in files]


def generate_typ(plates_dir: str, docopts: str = '',
                 template_rel: str = 'presswire_typst/presswire.typ') -> tuple:
    """读 plates → Typst 完整文本 + 版布局表。返回 (typ_text, layouts)。

    `template_rel`: 相对输出 .typ 文件的模板路径（任务 16 cli 接入时参数化；
    当前默认仓库根布局: out.typ 与 presswire_typst/ 同级）。
    """
    plates = _read_plates(plates_dir)
    data = render_plates_data(plates)
    typ_text = (
        data + '\n'
        f'#import "{template_rel}": render-doc\n'
        '#render-doc(plates)\n'
    )
    # layout.json 数据（pixelcheck --layout auto 消费）: main-aside → multi; 其他 → single
    layouts = {}
    for i, p in enumerate(plates, 1):
        layouts[f'p{i}'] = 'multi' if p.get('layout') == 'main-aside' else 'single'
    return typ_text, layouts


if __name__ == '__main__':
    import sys
    import tempfile

    # 自测: 空 plates 目录 → 空版占位可编译
    with tempfile.TemporaryDirectory() as td:
        # 空目录没有 .md → 应报错；先写一个最小 p1.md 验证数据生成
        import pathlib
        pathlib.Path(td, 'p1.md').write_text(
            'HEADLINE: 测试标题\nBODY:\n第一段。\n\n第二段 **加粗** 与 *斜体*。\n',
            encoding='utf-8')
        text, layouts = generate_typ(td)
        print(text)
        print('--- layouts:', layouts)
