// mainaside.typ — main-aside 版式（P1，任务 8；任务 10 重构用 atoms）
//
// 接口（7b 冻结）: render-mainaside(p, content-w, col-gap:) → content
// 由 render-doc 包进 plate-frame。
//
// 几何（latin linotype.cls mainaside 契约）:
//   main 宽  = 2/3·contentW − 1/3·colGap（两栏 + 沟 = mainW）
//   aside 宽 = 1/3·contentW − 2/3·colGap

#import "atoms.typ": kicker, headline, deck, byline, storybyline, pullquote, photo, inbrief

#let render-mainaside(p, content-w, col-gap: 3.75mm) = {
  let main-w = content-w * 2 / 3 - col-gap / 3
  let aside-w = content-w / 3 - col-gap * 2 / 3

  grid(
    columns: (main-w, col-gap, aside-w),
    [
      // ---- 主栏: 版头 + 正文两栏 ----
      #if p.at("kicker", default: "") != "" [ #kicker(p.at("kicker")) \ ]
      #if p.at("headline", default: "") != "" [ #headline(p.at("headline")) \ ]
      #if p.at("deck", default: "") != "" [ #deck(p.at("deck")) \ ]
      #if p.at("byline", default: "") != "" [ #byline(p.at("byline")) \ ]
      #v(4pt)
      #columns(2, gutter: col-gap)[
        // 图片（expM: 绝对宽，主栏半宽）
        #if p.at("image", default: "") != "" [
          #photo(
            p.at("image"),
            float(p.at("imagewidth", default: "1.0")),
            p.at("imagecaption", default: ""),
            main-w / 2,
          )
          #v(4pt)
        ]
        #for para in p.at("body", default: ()) [
          #par[#para]
        ]
        // 引文进主栏（latin 定案: pullquote → mainstory 正文末尾）
        #if p.at("pullquote", default: "") != "" [
          #v(3pt)
          #pullquote(p.at("pullquote"))
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
          #storybyline(st.at("byline")) \
        ]
        #for para in st.at("body", default: ()) [
          #par[#para]
        ]
      ]
      #let briefs = p.at("briefs", default: ())
      #if briefs.len() > 0 [
        #v(6pt)
        #line(length: 100%)
        #inbrief("IN BRIEF", briefs.slice(0, calc.min(3, briefs.len())))
      ]
    ],
  )
}
