// ============================================================
// P0 spike 实验 3: 中文长文溢出 (为 N1 提前验证)
// 验证 CJK 内容同样不推页、可测
// 运行:
//   typst compile p0-exp3-cjk.typ
//   typst query p0-exp3-cjk.typ --format json
// ============================================================

#set page(width: 420pt, height: 297pt, margin: 20pt)
#set text(size: 10pt, font: "Noto Serif CJK SC", lang: "zh")

#let zh-story = (
  "新闻报道的版面设计必须考虑中文排版的特点。中文文本没有单词之间的空格, 换行规则与西文不同。"
  + "在固定的报纸版心中, 当文章内容超过版心容量时, 版面编辑需要决定是裁剪内容、缩小字号还是将文章移到下一页。"
  + "本实验验证 Typst 的 block 组件在固定高度与裁剪模式下, 是否能够正确处理中文溢出内容而不推动页面。"
  + "对于自动化排版系统而言, 这一行为决定了版面容量测量与自动缩放的可行性。"
  + "如果 measure 函数能够返回中文内容在固定宽度下的自然高度, 那么系统就可以计算溢出量, 进而决定缩放策略。"
  + "本段文字被有意加长, 以确保其自然高度远超 100pt 的版心高度, 从而真正触发溢出与裁剪路径。"
  + "中文标点符号如句号。逗号, 问号? 感叹号! 均需正确处理, 避免出现悬挂标点或错误的换行位置。"
  + "以上内容再重复两遍以充分填充空间。新闻报道的版面设计必须考虑中文排版的特点。"
  + "中文文本没有单词之间的空格, 换行规则与西文不同。在固定的报纸版心中, 当文章内容超过版心容量时。"
  + "版面编辑需要决定是裁剪内容、缩小字号还是将文章移到下一页。本实验验证 Typst 的 block 组件。"
  + "在固定高度与裁剪模式下, 是否能够正确处理中文溢出内容而不推动页面。对于自动化排版系统而言。"
  + "这一行为决定了版面容量测量与自动缩放的可行性。如果 measure 函数能够返回中文内容在固定宽度下的自然高度。"
  + "那么系统就可以计算溢出量, 进而决定缩放策略。本段文字被有意加长, 以确保其自然高度远超版心高度。"
)

// ===== 渲染的固定版心 (中文) =====
#align(center)[
  #block(
    width: 150pt, height: 100pt, clip: true, breakable: false,
    stroke: 0.5pt + rgb("#888"),
    zh-story,
  ) #label("plate-CJK")
]

#v(6pt)

#line(length: 100%)
#text(size: 8pt, fill: gray)[footer — 中文溢出不推页]

#context {
  let pages-now = counter(page).get().last()
  let m-natural = measure(block(width: 150pt, zh-story))
  metadata((
    test: "exp3-cjk",
    box-width: 150pt,
    box-height: 100pt,
    pages-after-plate: pages-now,
    measure-natural-height: m-natural.height,
    deficit: m-natural.height - 100pt,
    fill: calc.min(100pt / m-natural.height, 1.0),
    overflow-detectable: m-natural.height > 100pt,
  ))
}
