// columns.typ — 等宽多栏版式（P2-P4，任务 8；任务 10 重构用 atoms）
//
// 接口（7b 冻结）: render-columns(p, content-w, col-gap:) → content
// 由 render-doc 包进 plate-frame（固定版心 + 溢出报告归 plate-frame）。

#import "atoms.typ": kicker, headline, subheadline, deck, byline, storybyline, expandedtitle, pullquote, photo, inbrief

#let render-columns(p, content-w, col-gap: 3.75mm) = {
  let n = if p.at("columns", default: "") == "" {
    3
  } else {
    int(p.at("columns"))
  }
  // 版头（通栏） + 正文多栏
  [
    #if p.at("kicker", default: "") != "" [ #kicker(p.at("kicker")) \ ]
    #if p.at("headline", default: "") != "" [ #headline(p.at("headline")) \ ]
    #if p.at("subheadline", default: "") != "" [ #subheadline(p.at("subheadline")) \ ]
    #if p.at("deck", default: "") != "" [ #deck(p.at("deck")) \ ]
    #if p.at("byline", default: "") != "" [ #byline(p.at("byline")) \ ]
    #if p.at("expanded", default: "") != "" [ #expandedtitle(p.at("expanded")) \ ]
    #v(4pt)
    #columns(n, gutter: col-gap)[
      // 图片（expM: 绝对宽）
      #if p.at("image", default: "") != "" [
        #photo(
          p.at("image"),
          float(p.at("imagewidth", default: "1.0")),
          p.at("imagecaption", default: ""),
          content-w / n,
        )
        #v(4pt)
      ]
      // 正文
      #for para in p.at("body", default: ()) [
        #par[#para]
      ]
      // 引文
      #if p.at("pullquote", default: "") != "" [
        #v(3pt)
        #pullquote(p.at("pullquote"))
      ]
      // 副故事
      #for st in p.at("stories", default: ()) [
        #v(3pt)
        #text(size: 11pt, weight: "bold")[#st.at("headline", default: "")]
        #if st.at("byline", default: "") != "" [
          #storybyline(st.at("byline")) \
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
          #inbrief("IN BRIEF", briefs.slice(g, calc.min(g + 3, briefs.len())))
          #if g + 3 < briefs.len() [ #v(3pt) ]
        ]
      ]
    ]
  ]
}
