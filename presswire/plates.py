"""plates.py — plates/*.md → 结构化 dict（契约层，任务 4）

从 latin 引擎 /home/yupeng/news/latex/build.py:76-150 逐行移植 `parse_plate`，
字段集/缺省值/类型/分割逻辑与 latin 逐字节等价（D2 红线: 不新增、不删除字段）。

输入格式（每版固定结构，见 latin build.py 头注释）:
    KICKER: ... / HEADLINE: ... / SUBHEADLINE: ... / DECK: ... / BYLINE: ...
    DATE: ... / LAYOUT: ... / COLUMNS: ... / EXPANDEDTITLE|EXPANDED: ...
    IMAGE: ... / IMAGEWIDTH: ... / IMAGECAPTION: ...
    BODY: (正文段, 段间空行)
    STORY-B|STORY-C: (可选副故事) HEADLINE: ... BYLINE-B: ... BODY: ...
    PULLQUOTE: ... (可选)
    BRIEFS: ... / MAINBRIEFS: ... (可选, 以换行分隔)

转义说明（契约层决策）: latin 的 parse_plate 在解析时就地调用 tex_escape
（`**bold**` → `\\textbf{bold}`、`&` → `\\&` 等），返回的 dict 值已转义。
本任务为保证与 latin 输出逐字节一致（对照验收），原样移植 tex_escape 为
`_escape()` 占位；任务 5（render_typst）将其替换为 Typst 转义——届时只改
这一个函数，解析层字段结构不动。
"""
import re

__all__ = ['parse_plate', '_strip_field', '_escape']


def _strip_field(s: str) -> str:
    """字段值去首尾空白（对应 latin build.py:49-50 strip_field）。"""
    return s.strip()


def _escape(s: str) -> str:
    """latin tex_escape（build.py:52-74）逐行移植——契约层占位。

    任务 5 替换为 Typst 转义（`\\``、`$`、`<`、`>` 等）；在此之前保持
    与 latin 完全相同的输出，保证 parse_plate 对照 diff 为零。
    血泪注释（源自 latin）: 先转义特殊字符（尤其 { }），再处理 markdown
    加粗/斜体，否则花括号被二次转义渲染成字面 "{"; 反斜杠用 \\x00 占位
    最后还原为 \\textbackslash{}，避免其 { } 被后续转义。
    """
    s = s.replace('\\', '\x00')
    s = s.replace('&', r'\&').replace('%', r'\%').replace('$', r'\$')
    s = s.replace('#', r'\#').replace('_', r'\_').replace('{', r'\{')
    s = s.replace('}', r'\}').replace('~', r'\textasciitilde{}')
    s = s.replace('^', r'\textasciicircum{}')
    # 中文弯引号 → LaTeX `` ''（英文直引号保留）
    s = s.replace('“', '``').replace('”', "''")
    # markdown 加粗 **x** → \textbf{x}（此时特殊字符已转义，花括号安全）
    s = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', s)
    # markdown 斜体 *x* → \textit{x}
    s = re.sub(r'(?<!\*)\*([^*]+?)\*(?!\*)', r'\\textit{\1}', s)
    # 还原反斜杠占位符（最后——\textbackslash{} 的 {} 不再经过 { } 转义）
    s = s.replace('\x00', r'\textbackslash{}')
    return s


def parse_plate(md_text: str, filename: str = '') -> dict:
    """解析单个 plates/pN.md → 结构化 dict（latin build.py:76-150 逐行移植）。

    `filename` 仅用于将来错误定位（当前不参与解析，保持与 latin 签名等价）。

    返回 dict 字段集（与 latin 完全一致，含默认值）:
        kicker/headline/subheadline/deck/byline/date/body/pullquote/briefs/
        mainbriefs/stories/layout/columns/expanded/image/imagewidth(默认
        '1.0')/imagecaption
        stories 内元素: {headline, body}（HEADLINE-in-story 分支另有
        byline: ''；BYLINE-B 填充之）——STORY-B/C 创建的 story 无 byline 键。
    """
    p = {'kicker': '', 'headline': '', 'subheadline': '', 'deck': '',
         'byline': '', 'date': '', 'body': [], 'pullquote': '', 'briefs': [],
         'mainbriefs': [],  # 2026-08-07: 主栏底部补白简讯（MAINBRIEFS 段，main-aside 用）
         'stories': [], 'layout': '', 'columns': '', 'expanded': '',
         'image': '', 'imagewidth': '1.0', 'imagecaption': ''}  # 图片: IMAGE 路径 / IMAGEWIDTH 比例(0-1) / IMAGECAPTION 图注
    lines = md_text.split('\n')
    section = 'body'
    story = None
    for ln in lines:
        ln = ln.rstrip()
        up = ln.strip().upper()
        if up.startswith('LAYOUT:'):
            p['layout'] = _strip_field(ln[7:]).lower(); section = 'meta'
        elif up.startswith('COLUMNS:'):
            p['columns'] = _strip_field(ln[8:]); section = 'meta'
        elif up.startswith('EXPANDEDTITLE:') or up.startswith('EXPANDED:'):
            p['expanded'] = _escape(_strip_field(ln.split(':', 1)[1])); section = 'meta'
        elif up.startswith('IMAGE:'):
            p['image'] = _strip_field(ln.split(':', 1)[1]); section = 'meta'
        elif up.startswith('IMAGEWIDTH:'):
            p['imagewidth'] = _strip_field(ln.split(':', 1)[1]); section = 'meta'
        elif up.startswith('IMAGECAPTION:'):
            p['imagecaption'] = _escape(_strip_field(ln.split(':', 1)[1])); section = 'meta'
        elif up.startswith('KICKER:'):
            p['kicker'] = _escape(_strip_field(ln[7:])); section = 'meta'
        elif up.startswith('HEADLINE:'):
            if section == 'story':
                # 副故事 headline（注意: latin 此处不转义，与主 headline 不同）
                if story: p['stories'].append(story)
                story = {'headline': _strip_field(ln[9:]), 'byline': '', 'body': []}
                section = 'story'
            else:
                p['headline'] = _escape(_strip_field(ln[9:])); section = 'meta'
        elif up.startswith('SUBHEADLINE:'):
            p['subheadline'] = _escape(_strip_field(ln[12:])); section = 'meta'
        elif up.startswith('DECK:'):
            p['deck'] = _escape(_strip_field(ln[5:])); section = 'meta'
        elif up.startswith('BYLINE:'):
            p['byline'] = _escape(_strip_field(ln[7:])); section = 'meta'
        elif up.startswith('DATE:'):
            # 2026-08-07 用户要求: 第一版页顶出版日期（\dateline 日期线）
            p['date'] = _escape(_strip_field(ln[5:])); section = 'meta'
        elif up.startswith('BYLINE-B:'):
            # 2026-08-07 用户要求: 副条(STORY-B)独立署名（日期/站点/记者）
            if story is not None:
                story['byline'] = _escape(_strip_field(ln[9:])); section = 'story'
        elif up.startswith('PULLQUOTE:'):
            p['pullquote'] = _escape(_strip_field(ln[10:])); section = 'meta'
        elif up.startswith('BRIEFS:'):
            section = 'briefs'
        elif up.startswith('MAINBRIEFS:'):
            # 2026-08-07: 主栏底部补白简讯段（P1 main-aside 用，前 2 条进
            # \mainstory 第 6/7 参 → 两栏底部）
            section = 'mainbriefs'
        elif up.startswith('STORY-B:') or up.startswith('STORY-C:'):
            if story: p['stories'].append(story)
            story = {'headline': _escape(_strip_field(ln.split(':', 1)[1])), 'body': []}
            section = 'story'
        elif up.startswith('BODY:'):
            section = 'body'
        elif ln.strip() == '':
            continue
        else:
            if section == 'body':
                p['body'].append(_escape(_strip_field(ln)))
            elif section == 'briefs':
                if ln.strip(): p['briefs'].append(_escape(_strip_field(ln)))
            elif section == 'mainbriefs':
                if ln.strip(): p['mainbriefs'].append(_escape(_strip_field(ln)))
            elif section == 'story' and story is not None:
                story['body'].append(_escape(_strip_field(ln)))
    if story: p['stories'].append(story)
    return p
