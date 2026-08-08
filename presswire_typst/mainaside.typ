// mainaside.typ — main-aside 版式（P1，任务 8；任务 10 重构用 atoms）
//
// 接口（7b 冻结）: render-mainaside(p, content-w, col-gap:) → content
// 由 render-doc 包进 plate-frame。
//
// 几何（latin linotype.cls mainaside 契约）:
//   main 宽  = 2/3·contentW − 1/3·colGap（两栏 + 沟 = mainW）
//   aside 宽 = 1/3·contentW − 2/3·colGap
//
// 2026-08-08 修复: 主栏内置 columns(2) 在固定 block 内不分栏（同 columns.typ
// 根因）→ 改用 split-columns（measure 贪心分组 + grid 并排）。
// 注意: Typst 数组 .push() 原地修改、返回 none。

#import "atoms.typ": kicker, headline, deck, byline, storybyline, pullquote, photo, inbrief
#import "columns.typ": split-columns

#let render-mainaside(p, content-w, col-gap: 3.75mm) = context {
  let main-w = content-w * 2 / 3 - col-gap / 3
  let aside-w = content-w / 3 - col-gap * 2 / 3
  let col-w = (main-w - col-gap) / 2  // 主栏两栏单栏宽

  // ---- 主栏元素（图片 → 正文 → 引文 → 主栏补白简讯）----
  let items = ()
  // 图片（expM: 绝对宽，主栏半宽）
  if p.at("image", default: "") != "" {
    items.push(block[
      #photo(
        p.at("image"),
        float(p.at("imagewidth", default: "1.0")),
        p.at("imagecaption", default: ""),
        col-w,
      )
      #v(4pt)
    ])
  }
  for para in p.at("body", default: ()) {
    // 块级公式标记 dict → 直接渲染（不包 par，段落内 block 被忽略）
    items.push(if type(para) == dictionary {
      para.at("__block-math__")
    } else {
      par[#para]
    })
  }
  // 引文进主栏（latin 定案: pullquote → mainstory 正文末尾）
  if p.at("pullquote", default: "") != "" {
    items.push(v(3pt) + pullquote(p.at("pullquote")))
  }
  // mainbriefs 主栏底部补白
  for item in p.at("mainbriefs", default: ()) {
    items.push(text(size: 8pt)[#item])
  }
  let groups = split-columns(items, 2, col-w)
  let main-cells = ([#for it in groups.at(0) [#it]], [], [#for it in groups.at(1) [#it]])

  grid(
    columns: (main-w, col-gap, aside-w),
    [
      // ---- 主栏: 版头 + 正文两栏 ----
      #if p.at("kicker", default: "") != "" [ #kicker(p.at("kicker")) \ ]
      #if p.at("headline", default: "") != "" [ #headline(p.at("headline")) \ ]
      #if p.at("deck", default: "") != "" [ #deck(p.at("deck")) \ ]
      #if p.at("byline", default: "") != "" [ #byline(p.at("byline")) \ ]
      #v(4pt)
      #grid(columns: (1fr, col-gap, 1fr), ..main-cells)
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
