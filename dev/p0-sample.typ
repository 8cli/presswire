// ============================================================
// P0 最小复现样本 → p0-sample.pdf
// 固定版心 150x100pt + 溢出裁剪 + label/metadata
// 编译: typst compile p0-sample.typ p0-sample.pdf
// ============================================================

#set page(width: 210pt, height: 160pt, margin: 8pt)
#set text(size: 9pt)

#let story = lorem(120)

#align(center)[
  #block(
    width: 150pt, height: 100pt, clip: true, breakable: false,
    stroke: 0.5pt + rgb("#888"),
    story,
  ) #label("plate-P1")
]

#v(4pt)

#context {
  let h = measure(block(width: 150pt, story)).height
  text(size: 7pt, fill: gray)[
    100pt box | measured natural height: #h | overflow: #(h - 100pt)
  ]
  metadata((
    plate: "P1",
    box-height: 100pt,
    natural-height: h,
    deficit: h - 100pt,
    fill: calc.min(100pt / h, 1.0),
  ))
}
