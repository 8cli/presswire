// atoms.typ — 排版原子（任务 10）
//
// 接口（7b 冻结，见 docs/contracts.md §2）: 原子只负责渲染（→ content），
// 不负责版心/measure（plate-frame 管）。所有原子第一参数为已转义字符串
// （plates.py `_escape`，code 字符串安全；富文本标记在 render_typst 生成
// 阶段已转 strong/emph content 表达式——见 contracts.md §5）。
//
// photo 原子（expM 定案）: IMAGEWIDTH（0-1 比例）× content-w = 绝对宽度
// （百分比 measure 解析为 0 的陷阱）；image 高度计入版心（measure 自然高）。

#import "theme.typ": theme-state

// ---- 版头原子 ----
#let kicker(txt) = context {
  let accent = theme-state.get().at("accent", default: rgb("#8C1D18"))
  text(size: 9pt, weight: "bold", fill: accent)[#txt]
}

#let headline(txt) = text(size: 15pt, weight: "bold")[#txt]

#let subheadline(txt) = text(size: 11pt, weight: "bold")[#txt]

#let deck(txt) = text(size: 10pt, style: "italic")[#txt]

#let byline(txt) = text(size: 8pt)[#txt]

#let storybyline(txt) = text(size: 8pt)[#txt]

#let dateline(txt) = text(size: 8pt)[#txt]

#let expandedtitle(txt) = text(size: 11pt, weight: "bold")[#txt]

// ---- 内容原子 ----
#let pullquote(txt) = context {
  let accent = theme-state.get().at("accent", default: rgb("#8C1D18"))
  block(stroke: (left: 2pt + accent), inset: (left: 6pt), width: 100%)[
    #text(size: 11pt, style: "italic")[#txt]
  ]
}

// photo: image-path + width-ratio（0-1 × content-w）+ caption 图注。
// 图片绝对宽 = ratio × 版心宽（expM: 百分比 measure=0 陷阱）。
#let photo(image-path, width-ratio, caption, content-w) = {
  let w = width-ratio * content-w
  block(width: 100%, breakable: false)[
    #image(image-path, width: w)
    #if caption != "" [
      #v(2pt)
      #text(size: 8pt, style: "italic")[#caption]
    ]
  ]
}

// brief: 简讯块（label + items 数组）
#let brief(label, items) = {
  v(3pt)
  text(size: 9pt, weight: "bold")[#label]
  linebreak()
  for item in items [
    #item
    #linebreak()
  ]
}

// inbrief: IN BRIEF 条（≤3 条一组，latin \inbrief 对应）
#let inbrief(label, items) = {
  text(size: 9pt, weight: "bold")[#label]
  linebreak()
  for item in items [
    #item
    #linebreak()
  ]
}
