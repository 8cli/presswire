// poster.typ — 画报版型（任务 13，N3）
//
// 调研（expP mini-spike 实证 2026-08-08）: Typst 生态无现成 2D 矩形拼版，
// 自研 place() 贪心装配（shelf worst-fit）——固定版心内可用、无重叠/
// 不越界/无空白带（12 板块实测通过）。place 在 layout 回调内可用，坐标
// 相对固定版心 block 内容区（原点 = 版心左上角）。
//
// 数据模型（D2 红线: 不新增 plates 字段）: 板块来源 = 现有字段——
//   IMAGE 单图（IMAGEWIDTH 比例）+ headline/deck/body 段/stories/briefs
//   文字板块；多图: body 段含 `![](path)` 标记（presswire 新能力，latin
//   无此标记——body 内为字面文本，见 render_typst 扩展）。
//
// 0.15 语法暗礁（expP）: 坐标/尺寸全程 float（pt 数值），发射时 ×1pt
// （length × length 不可用）；box() 无 align 参数。

#import "atoms.typ": headline, deck, byline, kicker

// ---- shelf worst-fit 贪心（expP 实证，float 坐标域）----
// item = (kind, w, h, c) 板块: 类型/宽/高/内容(float 宽高)
// shelf = (y, h, used) 行
#let shelf-worst-fit(items, W, H) = {
  let rows = ()
  let placed = ()
  for item in items {
    let w = item.w
    let h = item.h
    let best = none
    for i in range(rows.len()) {
      let r = rows.at(i)
      if W - r.used >= w and r.h >= h {
        if best == none or (W - r.used) > best.at(1) {
          best = (i, W - r.used)
        }
      }
    }
    if best != none {
      let i = best.at(0)
      let r = rows.at(i)
      placed.push((kind: item.kind, x: r.used, y: r.y, w: w, h: h, c: item.c))
      rows = range(rows.len()).map(k => {
        let rr = rows.at(k)
        if k == i { (y: rr.y, h: rr.h, used: rr.used + w) } else { rr }
      })
    } else {
      let y = if rows.len() == 0 {
        0.0
      } else {
        rows.at(rows.len() - 1).y + rows.at(rows.len() - 1).h
      }
      placed.push((kind: item.kind, x: 0.0, y: y, w: w, h: h, c: item.c))
      rows.push((y: y, h: h, used: w))
    }
  }
  (placed: placed, height: if rows.len() == 0 { 0.0 } else {
    rows.at(rows.len() - 1).y + rows.at(rows.len() - 1).h
  })
}

// ---- 画报版式 ----
// p: 版数据 dict; W/H: 版心尺寸(float pt); content-w: 版心宽(length)
#let render-poster(p, content-w, content-h) = {
  let W = content-w / 1pt   // float 版心宽
  let H = content-h / 1pt   // float 版心高
  let items = ()

  // 板块组装（按视觉优先级: 图片 → 标题 → 导语 → 正文 → 侧栏内容）
  // 1. IMAGE 图片板块（宽 60% 版心，高按比例）
  let img = p.at("image", default: "")
  if img != "" {
    items.push((
      kind: "image", w: W * 0.6, h: W * 0.6 * 0.6,
      c: [#image(img, width: W * 0.6 * 1pt)]
    ))
  }
  // 2. 标题板块（大字凌驾）
  if p.at("headline", default: "") != "" {
    items.push((kind: "text", w: W * 0.9, h: 40.0,
                c: [#headline(p.at("headline"))]))
  }
  // 3. 眉题 + 导语
  if p.at("kicker", default: "") != "" {
    items.push((kind: "text", w: W * 0.3, h: 18.0,
                c: [#kicker(p.at("kicker"))]))
  }
  if p.at("deck", default: "") != "" {
    items.push((kind: "text", w: W * 0.6, h: 30.0,
                c: [#deck(p.at("deck"))]))
  }
  // 4. 正文段（文字板块，含 body 内 ![](path) 图片标记 → 图片板块）
  for para in p.at("body", default: ()) {
    if type(para) == dictionary and para.at("__poster-img__", default: none) != none {
      items.push((kind: "image", w: W * 0.4, h: W * 0.4 * 0.6,
                  c: [#image(para.at("__poster-img__"), width: W * 0.4 * 1pt)]))
    } else {
      items.push((kind: "text", w: W * 0.95, h: 20.0, c: [#par[#para]]))
    }
  }
  // 5. 副故事/简讯（侧栏风格小板块）
  for st in p.at("stories", default: ()) {
    items.push((kind: "text", w: W * 0.5, h: 16.0,
                c: [#text(size: 10pt)[#st.at("headline", default: "")]]))
  }

  // 贪心装配 → place 发射（坐标 float → ×1pt）
  context {
    let plan = shelf-worst-fit(items, W, H)
    let placed = plan.placed
    // 空版心防护: 无板块直接返回空
    if placed.len() == 0 { return [] }
    // 发射前用 block 占位版心（clip 含住溢出）
    block(width: content-w, height: content-h, clip: true, breakable: false)[
      #for p in placed [
        #place(dx: p.x * 1pt, dy: p.y * 1pt, p.c)
      ]
    ]
  }
}
