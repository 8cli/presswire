// ============================================================
// P0 spike 实验 2 (v2): label + metadata → typst query 通道
// 修正: 每个 label 只出现一次; label 放在块内部
// 验证 query 取 fill/deficit 数值的可靠通道
// 运行:
//   typst query p0-exp2-query.typ "<plate-P1>" --format json
//   typst query p0-exp2-query.typ "<meta-P1>" --field value
//   typst eval 'query(<plate-P1>)' --in p0-exp2-query.typ   (非弃用通道)
// ============================================================

#set page(width: 420pt, height: 297pt, margin: 20pt)

// 结构化 metadata: 模拟版面测量结果 (fill 比率 + deficit 长度)
#metadata((plate: "P1", fill: 0.9, deficit: 12.5pt, overflow: true))
#label("meta-P1")

#v(10pt)

// 块内打 label: 可查位置/结构, 但 block 无 value 字段
#block(
  width: 150pt, height: 60pt, stroke: 0.5pt + gray,
  [Plate block #label("plate-P1")],
)

#v(6pt)

// 独立 label 元素
#label("plate-P2")
