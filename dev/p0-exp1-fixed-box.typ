// ============================================================
// P0 spike 实验 1: 固定版心不推页 + measure 溢出可测
// Typst 0.15.1
// 运行:
//   typst compile p0-exp1-fixed-box.typ
//   typst query p0-exp1-fixed-box.typ --format json
// ============================================================

#set page(width: 420pt, height: 297pt, margin: 20pt)
#set text(size: 10pt)

// 大量内容: 自然高度远超整页内容区(257pt), 用于证明 clip 裁剪而非推页
#let story = lorem(400)

// ===== 渲染的固定版心: 150x100pt, clip 裁剪, breakable 禁止 =====
#align(center)[
  #block(
    width: 150pt,
    height: 100pt,
    clip: true,
    breakable: false,
    stroke: 0.5pt + rgb("#888"),
    story,
  ) #label("plate-P1")
]

#v(6pt)

#line(length: 100%)
#text(size: 8pt, fill: gray)[footer line — 固定版心 clip 生效, 溢出内容应被裁剪而非推页]

// ===== 页数快照 + 三种 measure 测法对比 =====
#context {
  let pages-now = counter(page).get().last()
  let box-h = 100pt
  // 测法 A: 直接量渲染的固定盒(含固定高+clip) —— 预期返回固定 100pt, 无法暴露溢出
  let m-fixed = measure(block(width: 150pt, height: 100pt, clip: true, story))
  // 测法 B(深度块测, 绕行#7779的推荐路径): 只给宽度约束, 量自然高度
  let m-natural = measure(block(width: 150pt, story))
  // 测法 C: measure 直接给 width 参数
  let m-text = measure(story, width: 150pt)
  metadata((
    test: "exp1-fixed-box",
    box-width: 150pt,
    box-height: box-h,
    pages-after-plate: pages-now,
    measure-A-fixed-clip-height: m-fixed.height,
    measure-B-natural-height: m-natural.height,
    measure-C-width-param-height: m-text.height,
    deficit: m-natural.height - box-h,
    fill: calc.min(100pt / m-natural.height, 1.0),
    overflow-detectable: m-natural.height > box-h,
  ))
}
