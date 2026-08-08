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

#let themes = (
  // broadsheet（默认，对应 latin newspaper）: 衬线 + 深红
  "broadsheet": (
    body-font: ("Noto Serif CJK SC", "Libertinus Serif", "New Computer Modern"),
    display-font: ("Noto Serif CJK SC", "Libertinus Serif"),
    accent: rgb("#8C1D18"),
    ink: rgb("#1A1A1A"),
  ),
  // magazine: 深蓝强调（latin magazine 契约）
  "magazine": (
    body-font: ("Noto Serif CJK SC", "Libertinus Serif", "New Computer Modern"),
    display-font: ("Noto Serif CJK SC", "Libertinus Serif"),
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
