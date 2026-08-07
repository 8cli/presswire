// ============================================================
// P0 spike 实验 1c 对照: 固定高度 + 无 clip → 溢出是否在页内溢出(不推页)?
// 观察: 固定高度本身即阻止推页; clip 只决定溢出可见还是隐藏
// 渲染 PNG 目检 + pdfinfo 页数
// 运行: typst compile p0-exp1c-spill.typ --format png
// ============================================================

#set page(width: 420pt, height: 297pt, margin: 20pt)
#set text(size: 10pt)

#let story = lorem(400)

// 场景 B: 固定高度 100pt + breakable:true + 无 clip
#block(
  width: 150pt, height: 100pt,
  breakable: true,
  stroke: 0.5pt + blue,
  story,
)

// 紧随其后的对照线: 若内容页内溢出, 会与此线重叠
#line(length: 100%)
#text(size: 8pt, fill: red)[--- 对照线: 固定高度块后的下一条内容 ---]

#context metadata((test: "exp1c-spill", scenario: "fixed-height-no-clip", final-pages: counter(page).get().last()))
