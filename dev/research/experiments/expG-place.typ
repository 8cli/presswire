// ============================================================
// 实验 G: place() 绝对定位机制（任务 13 画报排版前置验证）
// 验证: place 坐标系、相对位置、重叠、z-order
// ============================================================
#set page(width: 300pt, height: 300pt, margin: 20pt)

// 场景 A: place 的坐标系 —— 相对页面? 相对容器?
#place(
  dx: 0pt, dy: 0pt,
  box(width: 60pt, height: 60pt, fill: rgb("#f66"))[A 左上],
)

// 场景 B: dx/dy 偏移
#place(
  dx: 40pt, dy: 40pt,
  box(width: 60pt, height: 60pt, fill: rgb("#6f6"))[B 偏移],
)

// 场景 C: 相对位置 place(right+top)
#place(
  right + top,
  box(width: 60pt, height: 60pt, fill: rgb("#66f"))[C 右上],
)

// 场景 D: 重叠与 z-order（后放的压先放的?）
#place(
  dx: 100pt, dy: 150pt,
  box(width: 80pt, height: 80pt, fill: rgb("#ff0"))[D1],
)
#place(
  dx: 120pt, dy: 170pt,
  box(width: 60pt, height: 60pt, fill: rgb("#f0f"))[D2 压上?],
)

// 场景 E: place 在 block 内是否相对 block 定位
#block(width: 150pt, height: 100pt, stroke: 0.5pt + gray)[
  块内文本
  #place(dx: 80pt, dy: 50pt, box(width: 40pt, height: 30pt, fill: rgb("#0ff")))
]

#context metadata((
  "test": "expG-place",
  "final-pages": counter(page).get().last(),
))
