// ============================================================
// P0 spike 实验 1b 对照: 无固定高度(普通流式 block) → 溢出推页
// 反证实验 1: 固定版心 clip+breakable:false 不推页
// 运行: typst compile p0-exp1b-push.typ && pdfinfo ...
// ============================================================

#set page(width: 420pt, height: 297pt, margin: 20pt)
#set text(size: 10pt)

#let story = lorem(400)

// 场景 A: 自动高度 + breakable 默认(true) → 内容按页流动, 必然多页
#block(
  width: 150pt,
  stroke: 0.5pt + blue,
  story,
)

#context metadata((test: "exp1b-push-contrast", scenario: "auto-height-breakable", final-pages: counter(page).get().last()))
