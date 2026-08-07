// ============================================================
// P0 spike 实验 4 (补充): typst#7779 风险边界实证
// 检查 measure 对「宽度溢出」内容的处理 —— 这正是计划中提到的潜在阻断点
// 运行: typst query p0-exp4-width-risk.typ --format json
// ============================================================

#set page(width: 420pt, height: 297pt, margin: 20pt)
#set text(size: 10pt)

#context {
  // 场景 A: 150pt 宽块内放 300pt 宽内层盒 → 横向溢出
  let a-height = measure(block(width: 150pt, box(width: 300pt, height: 30pt, fill: rgb("#faa")))).height
  // 场景 B: 不可换行长串 (西文无空格单词) 超宽
  let long-word = text(font: "Libertinus Mono")[WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW]
  let b-height = measure(block(width: 150pt, long-word)).height
  let b-width = measure(block(width: 150pt, long-word)).width
  // 场景 C: 正常可换行文本 (对照)
  let c-height = measure(block(width: 150pt, lorem(20))).height
  let c-width = measure(block(width: 150pt, lorem(20))).width
  // 场景 D: 直接 measure 不带宽度约束的溢出盒(看是否返回自然宽)
  let d-width = measure(box(width: 300pt, height: 30pt)).width

  metadata((
    test: "exp4-width-risk",
    scenario-A-inner-300pt-box: (
      block-constraint: 150pt,
      measured-height: a-height,
    ),
    scenario-B-unbreakable-long-word: (
      measured-height: b-height,
      measured-width: b-width,
      line-count-clue: b-height / 11.8pt,
    ),
    scenario-C-normal-text: (
      measured-height: c-height,
      measured-width: c-width,
    ),
    scenario-D-naked-overflow-box: (
      measured-width: d-width,   // 期望 300pt (自然宽)
    ),
  ))
}
