// mainaside.typ — main-aside 版式（P1，任务 8）
//
// 接口（7b 冻结，2026-08-08 扩展: 增加 content-w/col-gap 参数）:
//   render-mainaside(p, content-w, col-gap:) → content
//     p:          版数据 dict（plates 数组元素）
//     content-w:  版心宽（render-doc 传入）
//     col-gap:    栏缝（latin \colGap = 3.75mm）
// 由 render-doc 包进 plate-frame。
//
// 几何（latin linotype.cls mainaside 契约）:
//   main 宽  = 2/3·contentW − 1/3·colGap（两栏 + 沟 = mainW）
//   aside 宽 = 1/3·contentW − 2/3·colGap
// 主栏: 版头 + 正文 columns(2)；侧栏: stories + IN BRIEF。
// mainbriefs: 主栏底部补白（任务 8 简化: 排在主栏正文后；栏底对齐归任务 11）。
//
// 注（2026-08-08 决策）: expL 的 state() 收集器对 presswire 结构化 plates
// 数据模型非必需——stories/briefs 已在 p['stories']/p['briefs'] 数组中，
// 直接渲染进侧栏即可（state 收集器适用于内容散落在文档流的场景）。

#let render-mainaside(p, content-w, col-gap: 3.75mm) = {
  let main-w = content-w * 2 / 3 - col-gap / 3
  let aside-w = content-w / 3 - col-gap * 2 / 3

  grid(
    columns: (main-w, col-gap, aside-w),
    [
      // ---- 主栏: 版头 + 正文两栏 ----
      #if p.at("kicker", default: "") != "" [
        #text(size: 9pt, weight: "bold")[#p.at("kicker")] \
      ]
      #if p.at("headline", default: "") != "" [
        #text(size: 15pt, weight: "bold")[#p.at("headline")] \
      ]
      #if p.at("deck", default: "") != "" [
        #text(size: 10pt, style: "italic")[#p.at("deck")] \
      ]
      #if p.at("byline", default: "") != "" [
        #text(size: 8pt)[#p.at("byline")] \
      ]
      #v(4pt)
      #columns(2, gutter: col-gap)[
        #for para in p.at("body", default: ()) [
          #par[#para]
        ]
        // 引文进主栏（latin 定案: pullquote → mainstory 正文末尾）
        #if p.at("pullquote", default: "") != "" [
          #v(3pt)
          #block(stroke: (left: 2pt + black), inset: (left: 6pt), width: 100%)[
            #text(size: 11pt, style: "italic")[#p.at("pullquote")]
          ]
        ]
        // mainbriefs 主栏底部补白
        #for item in p.at("mainbriefs", default: ()) [
          #v(2pt)
          #text(size: 8pt)[#item]
        ]
      ]
    ],
    [],
    [
      // ---- 侧栏: 副故事 + IN BRIEF ----
      #for (si, st) in p.at("stories", default: ()).enumerate() [
        #if si > 0 [ #v(6pt) #line(length: 100%) ]
        #text(size: 11pt, weight: "bold")[#st.at("headline", default: "")]
        #if st.at("byline", default: "") != "" [
          #text(size: 8pt)[#st.at("byline")] \
        ]
        #for para in st.at("body", default: ()) [
          #par[#para]
        ]
      ]
      #let briefs = p.at("briefs", default: ())
      #if briefs.len() > 0 [
        #v(6pt)
        #line(length: 100%)
        #text(size: 9pt, weight: "bold")[IN BRIEF] \
        #for item in briefs.slice(0, calc.min(3, briefs.len())) [
          #item \
        ]
      ]
    ],
  )
}
