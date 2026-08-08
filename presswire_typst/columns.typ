// columns.typ — 等宽多栏版式（P2-P4，任务 8）
//
// 接口（7b 冻结，2026-08-08 扩展: 增加 content-w/col-gap 参数）:
//   render-columns(p, content-w, col-gap:) → content
//     p:          版数据 dict（plates 数组元素）
//     content-w:  版心宽（render-doc 传入 = paperW − 2·padSide）
//     col-gap:    栏缝（latin \colGap = 3.75mm）
// 由 render-doc 包进 plate-frame（固定版心 + 溢出报告归 plate-frame）。
//
// 版式: 版头（kicker/headline/subheadline/deck/byline/expanded）通栏 +
// 正文 columns(n) 多栏（n 由 p.columns 驱动，latin \begin{storycolumns}[n] 对应）。
// pullquote/stories/briefs 全进栏内（expR spike 实证: columns 固定块内可用）。

#let render-columns(p, content-w, col-gap: 3.75mm) = {
  let n = if p.at("columns", default: "") == "" {
    3
  } else {
    int(p.at("columns"))
  }
  // 版头（通栏） + 正文多栏
  [
    #if p.at("kicker", default: "") != "" [
      #text(size: 9pt, weight: "bold")[#p.at("kicker")] \
    ]
    #if p.at("headline", default: "") != "" [
      #text(size: 15pt, weight: "bold")[#p.at("headline")] \
    ]
    #if p.at("subheadline", default: "") != "" [
      #text(size: 11pt, weight: "bold")[#p.at("subheadline")] \
    ]
    #if p.at("deck", default: "") != "" [
      #text(size: 10pt, style: "italic")[#p.at("deck")] \
    ]
    #if p.at("byline", default: "") != "" [
      #text(size: 8pt)[#p.at("byline")] \
    ]
    #if p.at("expanded", default: "") != "" [
      #text(size: 11pt, weight: "bold")[#p.at("expanded")] \
    ]
    #v(4pt)
    #columns(n, gutter: col-gap)[
      // 正文
      #for para in p.at("body", default: ()) [
        #par[#para]
      ]
      // 引文
      #if p.at("pullquote", default: "") != "" [
        #v(3pt)
        #block(stroke: (left: 2pt + black), inset: (left: 6pt), width: 100%)[
          #text(size: 10pt + 1pt, style: "italic")[#p.at("pullquote")]
        ]
      ]
      // 副故事
      #for st in p.at("stories", default: ()) [
        #v(3pt)
        #text(size: 11pt, weight: "bold")[#st.at("headline", default: "")]
        #if st.at("byline", default: "") != "" [
          #text(size: 8pt)[#st.at("byline")] \
        ]
        #for para in st.at("body", default: ()) [
          #par[#para]
        ]
      ]
      // 简讯（每 3 条一组 IN BRIEF）
      #let briefs = p.at("briefs", default: ())
      #if briefs.len() > 0 [
        #v(3pt)
        #for g in range(0, briefs.len(), step: 3) [
          #text(size: 9pt, weight: "bold")[IN BRIEF] \
          #for item in briefs.slice(g, calc.min(g + 3, briefs.len())) [
            #item \
          ]
          #if g + 3 < briefs.len() [ #v(3pt) ]
        ]
      ]
    ]
  ]
}
