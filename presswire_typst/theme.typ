// theme.typ — 主题预设（任务 9）
//
// 模型: 主题 = 字体（body/display）+ 强调色 accent + 正文字色 ink。
// latin linotype.cls 对应（bodyfont/displayfont/accent/ink）。
//
// 传递机制（2026-08-08 实测）:
//   - 字体: render-doc 参数展开（set text 需直接求值，非 context）
//   - accent/ink: 经 state 传递——`show 自定义函数` 非法（only element
//     functions can be used as selectors，实测），atoms 内 context 读 state
//
// 用法: render-doc(plates, theme: "magazine")；atoms 读
//   #let accent = theme-value("accent", default: rgb("#8C1D18"))
//
// 2026-08-08 修复（真实出报首跑）: body-font 原为 Noto Serif CJK SC 优先——
// 纯英文板材也走 CJK 字体（英文 glyph 更宽，版面容量浪费 20-30%，P4 实测
// 953pt vs 733pt）。改 Libertinus Serif 优先（英文衬线，CJK 内容经字体回退
// 自动走 Noto——Typst 按字符回退，中英混排不受影响）。

#let themes = (
  // broadsheet（默认，对应 latin newspaper）: 衬线正文 + 无衬线标题 + 深红
  // 2026-08-08 用户决策: 标题（headline/kicker/deck）换无衬线（报纸通行
  // 风格: 正文衬线 + 标题黑体，如 Franklin Gothic 类）。Liberation Sans
  // = Arial 度量兼容（Typst 内置），中文回退 Noto Sans CJK SC。
  "broadsheet": (
    body-font: ("Libertinus Serif", "Noto Serif CJK SC", "New Computer Modern"),
    display-font: ("Liberation Sans", "Noto Sans CJK SC"),
    accent: rgb("#8C1D18"),
    ink: rgb("#1A1A1A"),
  ),
  // magazine: 深蓝强调（latin magazine 契约）
  "magazine": (
    body-font: ("Libertinus Serif", "Noto Serif CJK SC", "New Computer Modern"),
    display-font: ("Liberation Sans", "Noto Sans CJK SC"),
    accent: rgb("#1B3A5C"),
    ink: rgb("#1A1A1A"),
  ),
)

#let theme-state = state("presswire-theme", themes.at("broadsheet"))

// 更新主题 state 并返回 body（render-doc 调用）
#let apply-theme(theme-name, body) = {
  let t = themes.at(theme-name, default: themes.at("broadsheet"))
  theme-state.update(t)
  body
}
