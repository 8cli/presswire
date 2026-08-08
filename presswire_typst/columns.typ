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

#import "atoms.typ": kicker, headline, subheadline, deck, byline, storybyline, storyheadline, expandedtitle, pullquote, photo, inbrief

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
  // ---- 平衡（2026-08-08 用户反馈: 栏底不齐、矮栏下部大片留白）----
  // 贪心只按"累计 ≥ target 切"，元素粒度粗 → 前几栏满、末栏空。
  // 后处理: 反复从最高栏取出**最小可移动元素**（尺寸最接近补缺量的），
  // 放入最低栏，直到栏高差 < 50pt 或无法再移。取最小元素而非末尾——
  // 末尾元素可能是大块（STORY 段），移走会让高栏骤降、低栏骤增（震荡）。
  // 阅读顺序大体保持（块级移动，报纸跨栏续读可接受）。
  let col-height = groups.map(g =>
    g.map(it => measure(it, width: col-w).height + lead).fold(0pt, (a, b) => a + b))
  let guard = 0
  while guard < 20 {
    let hi = 0
    let lo = 0
    for i in range(n) {
      if col-height.at(i) > col-height.at(hi) { hi = i }
      if col-height.at(i) < col-height.at(lo) { lo = i }
    }
    if col-height.at(hi) - col-height.at(lo) < 50pt { break }
    // 最高栏找最小元素（避免移大块造成震荡）
    let hi-group = groups.at(hi)
    let lo-group = groups.at(lo)
    let pick = -1
    let pick-h = (col-height.at(hi) - col-height.at(lo))  // 目标: 移走 ≈ 差的一半
    let best = 1e10pt
    for i in range(hi-group.len()) {
      let h = measure(hi-group.at(i), width: col-w).height + lead
      let dist = calc.abs(h - pick-h / 2)
      if h < best and h < col-height.at(hi) - col-height.at(lo) {
        best = h
        pick = i
      }
    }
    if pick < 0 { break }
    let moved = hi-group.remove(pick)
    lo-group.push(moved)
    let new-groups = ()
    for i in range(n) {
      if i == hi {
        new-groups.push(hi-group)
      } else if i == lo {
        new-groups.push(lo-group)
      } else {
        new-groups.push(groups.at(i))
      }
    }
    groups = new-groups
    let calc = g => g.map(it => measure(it, width: col-w).height + lead)
      .fold(0pt, (a, b) => a + b)
    let nh = ()
    for i in range(n) {
      if i == hi or i == lo {
        nh.push(calc(groups.at(i)))
      } else {
        nh.push(col-height.at(i))
      }
    }
    col-height = nh
    guard += 1
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
  // 2026-08-08 修复: grid 总宽 = content-w − INK-MARGIN——文字字形 ink 会
  // 超出词框（斜体/粗体/尾字母），grid 总宽 = block 宽时 ink 贴 block 右缘
  // 被 clip 裁剪（用户视觉验收发现）。右侧留 4pt ink 边距，任何 ink 外伸
  // 都在 block 内。
  let INK-MARGIN = 4pt
  let col-w = (content-w - INK-MARGIN - col-gap * (n - 1)) / n
  // 2026-08-08 修复: grid 列宽用显式 col-w（非 1fr）——1fr 等分与 measure
  // 不一致导致渲染栏高 > measure 栏高（实测差 150pt+），平衡算法基于
  // measure 失效、内容堆栏0。显式列宽 = measure 宽度，渲染与 measure 一致。
  let grid-cols = ()
  for i in range(n) {
    if i > 0 { grid-cols.push(col-gap) }
    grid-cols.push(col-w)
  }
  // grid 总宽 = content-w - INK-MARGIN（1fr 自动分配）
  let grid-total = content-w - INK-MARGIN
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
    // 2026-08-08 修复: STORY 块拆段——整块（标题+署名+正文）作为单元素时
    // 大块（如 395pt Tianwen）无法平衡（放哪栏哪栏超载）。拆成标题块 +
    // 每正文段独立元素，平衡可细粒度移动段落 → 栏底齐平。
    items.push(v(3pt) + storyheadline(st.at("headline", default: "")))
    if st.at("byline", default: "") != "" {
      items.push(storybyline(st.at("byline")))
    }
    for para in st.at("body", default: ()) {
      items.push(par[#para])
    }
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
    // grid 容器宽 = grid-total（content-w − ink 边距）→ 栏宽 = col-w，文字不贴边
    #block(width: grid-total)[#grid(columns: grid-cols, ..grid-cells(groups))]
  ]
}
