// ============================================================
// 实验 D: measure 对宽度溢出的精确行为（#7779 彻底验证）
// 验证: 有宽度约束的块测高, 内层内容超宽时 measure 返回什么
// ============================================================
#set page(width: 420pt, height: 297pt, margin: 20pt)
#set text(size: 10pt)

#context {
  // 场景 A: 150pt 约束 + 300pt 宽内层盒（横向溢出）
  let a-h = measure(block(width: 150pt, box(width: 300pt, height: 30pt))).height
  let a-w = measure(block(width: 150pt, box(width: 300pt, height: 30pt))).width
  // 场景 B: 不可换行长串
  let long = text(font: "DejaVu Sans Mono")[WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW]
  let b-h = measure(block(width: 150pt, long)).height
  let b-w = measure(block(width: 150pt, long)).width
  // 场景 C: measure 直接给 width 参数（P0 测法 C）
  let c-h = measure(block(width: 150pt, box(width: 300pt, height: 30pt)), width: 150pt).height
  // 场景 D: 无约束盒（自然宽）
  let d-w = measure(box(width: 300pt, height: 30pt)).width
  // 场景 E: text 直接测宽
  let e-w = measure(long, width: 150pt).width

  metadata((
    "test": "expD-measure-width",
    "A-block-w150-h300box-height": a-h,
    "A-block-width": a-w,
    "B-longword-block-height": b-h,
    "B-longword-block-width": b-w,
    "C-measure-width-param-height": c-h,
    "D-naked-box-width": d-w,
    "E-longword-measure-width-param": e-w,
  ))
}
