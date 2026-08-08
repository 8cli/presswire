// columns.typ — 等宽多栏版式（P2-P4，任务 8；任务 10 重构用 atoms）
//
// 接口（7b 冻结）: render-columns(p, content-w, col-gap:) → content
// 由 render-doc 包进 plate-frame（固定版心 + 溢出报告归 plate-frame）。
//
// 2026-08-08 修复（真实出报首跑发现，三次迭代）:
//   ① 内置 columns() 是**页面级**布局函数，在 plate-frame 的固定 block 内
//      不分栏（expR 误判——lorem 行长随机掩盖；autofit 缩放时代更掩盖）→
//      改手动分栏。
//   ② 区段式（主条/副条/简讯各自独立 grid 行）→ 浪费栏空间（总高超）。
//   ③ **单连续流 + inbrief 拆条**（终版）: 全部内容（正文→引文→副条→
//      简讯条）一个顺序流，measure 贪心切栏——简讯条分散进各栏底部，
//      栏高均衡 + 阅读顺序保持 + 版心用满。grid 是块级布局，measure 准确。
// 注意: Typst 数组 .push() 原地修改、返回 none（勿写 items = items.push(...)）。

#import "atoms.typ": kicker, headline, subheadline, deck, byline, storybyline, expandedtitle, pullquote, photo, inbrief

// ---- 手动分栏（measure 贪心，须在 context 内调用）----
// items: content 元素数组；n: 栏数；col-w: 单栏宽
// 返回: 每栏元素数组的数组（累计高度超 总高/n 即切栏，顺序保持 + 栏高均衡）
#let split-columns(items, n, col-w) = {
  let lead = 3pt  // 元素间距近似（v(3pt)）
  let heights = items.map(it => measure(it, width: col-w).height + lead)
  let total = heights.fold(0pt, (a, b) => a + b)
  let groups = ()
  let cur = ()
  let acc = 0pt
  if items.len() <= n {
    // 元素少于栏数 → 每栏至多一个（不切段）
    for i in range(n) {
      if i < items.len() { cur.push(items.at(i)) }
      groups.push(cur)
      cur = ()
    }
  } else {
    let target = total / n
    for i in range(items.len()) {
      cur.push(items.at(i))
      acc += heights.at(i)
      if groups.len() < n - 1 and acc >= target and i < items.len() - 1 {
        groups.push(cur)
        cur = ()
        acc = 0pt
      }
    }
    groups.push(cur)
    while groups.len() < n { groups.push(()) }
  }
  groups
}

// ---- grid 单元格（栏数组 → grid 列参数，中间插 gutter 空列）----
#let grid-cells(groups) = {
  let cells = ()
  for gi in range(groups.len()) {
    if gi > 0 { cells.push([]) }
    cells.push([#for it in groups.at(gi) [#it]])
  }
  cells
}

#let render-columns(p, content-w, col-gap: 3.75mm) = context {
  let n = if p.at("columns", default: "") == "" {
    3
  } else {
    int(p.at("columns"))
  }
  let col-w = (content-w - col-gap * (n - 1)) / n
  let grid-cols = (1fr,)
  for i in range(1, n) {
    grid-cols.push(col-gap)
    grid-cols.push(1fr)
  }
  // ---- 单连续流元素（顺序: 图片 → 正文 → 引文 → 副条 → IN BRIEF 条）----
  let items = ()
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
  if p.at("pullquote", default: "") != "" {
    items.push(v(3pt) + pullquote(p.at("pullquote")))
  }
  for st in p.at("stories", default: ()) {
    items.push(block[
      #v(3pt)
      #text(size: 11pt, weight: "bold")[#st.at("headline", default: "")]
      #if st.at("byline", default: "") != "" [
        #storybyline(st.at("byline")) \
      ]
      #for para in st.at("body", default: ()) [
        #par[#para]
      ]
    ])
  }
  // 简讯拆条（每 3 条一组 IN BRIEF 块太大 → 单条元素，label 只在首条）
  let briefs = p.at("briefs", default: ())
  for (bi, b) in briefs.enumerate() {
    items.push(if bi == 0 {
      v(3pt) + text(size: 9pt, weight: "bold")["IN BRIEF"] + linebreak() + b
    } else {
      v(3pt) + b
    })
  }
  // ---- 分栏 + grid 渲染 ----
  let groups = split-columns(items, n, col-w)
  [
    // 版头（通栏）
    #if p.at("kicker", default: "") != "" [ #kicker(p.at("kicker")) \ ]
    #if p.at("headline", default: "") != "" [ #headline(p.at("headline")) \ ]
    #if p.at("subheadline", default: "") != "" [ #subheadline(p.at("subheadline")) \ ]
    #if p.at("deck", default: "") != "" [ #deck(p.at("deck")) \ ]
    #if p.at("byline", default: "") != "" [ #byline(p.at("byline")) \ ]
    #if p.at("expanded", default: "") != "" [ #expandedtitle(p.at("expanded")) \ ]
    #v(4pt)
    #grid(columns: grid-cols, ..grid-cells(groups))
  ]
}
