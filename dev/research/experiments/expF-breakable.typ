// ============================================================
// 实验 F: breakable 对固定高度 block 的语义（版心纪律完整画像）
// 验证: 固定高度块 + breakable 变体的行为（P0 exp1/1b/1c 的补全）
// ============================================================
#set page(width: 420pt, height: 297pt, margin: 20pt)
#set text(size: 10pt)

#let story = lorem(300)

// 场景 A: 固定高 + clip + breakable:false（presswire 目标配置, P0 exp1 已验）
#block(width: 150pt, height: 100pt, clip: true, breakable: false, stroke: 0.5pt + rgb("#888"))[#story #label("blk-A")]
#v(4pt)
#text(size: 8pt, fill: gray)[A: fixed+clip+nonbreakable]

#v(8pt)

// 场景 B: 固定高 + clip + breakable:true（允许跨页?）
#block(width: 150pt, height: 100pt, clip: true, breakable: true, stroke: 0.5pt + blue)[#story #label("blk-B")]
#v(4pt)
#text(size: 8pt, fill: gray)[B: fixed+clip+breakable]

#v(8pt)

// 场景 C: 固定高 + 无 clip + breakable:true（P0 exp1c 已验 1 页）
#block(width: 150pt, height: 100pt, breakable: true, stroke: 0.5pt + blue)[#story #label("blk-C")]
#v(4pt)
#text(size: 8pt, fill: gray)[C: fixed+no-clip+breakable]

#context metadata((
  "test": "expF-breakable",
  "final-pages": counter(page).get().last(),
))

#context {
  let pages = counter(page).get().last()
  metadata((
    "blk-A-page": query(<blk-A>).at(0).location().page(),
    "blk-B-page": query(<blk-B>).at(0).location().page(),
    "blk-C-page": query(<blk-C>).at(0).location().page(),
    "total-pages": pages,
  ))
}

