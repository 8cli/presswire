// ============================================================
// 实验 O1: 中文标题在固定栏宽的换行/超宽行为（任务 15）
// ============================================================
#set page(width: 400pt, height: 400pt, margin: 15pt)
#set text(font: "Noto Serif CJK SC", lang: "zh")

#let t1 = "三中全会部署进一步全面深化改革"
#let t2 = "China's Economy Shows Resilience Amid Global Uncertainties"
#let t3 = "国产大飞机C919完成商业首航 Beijing-Shanghai"

#context {
  // 无约束自然宽（单行）
  let w1 = measure(text(t1)).width
  let w2 = measure(text(t2)).width
  // 有约束 150pt 下的高度（换行数线索）
  let h1 = measure(text(t1), width: 150pt).height
  let h2 = measure(text(t2), width: 150pt).height

  metadata((
    "test": "expO1-headline-width",
    "zh-natural-w": w1,
    "en-natural-w": w2,
    "zh-h-at-150pt": h1,
    "en-h-at-150pt": h2,
    "zh-lines-clue": h1 / 16.2,   // 行高约 16.2pt (11pt字)
    "en-lines-clue": h2 / 16.2,
  ))
}

// 渲染对照: 150pt 宽块内的标题换行
#text(size: 11pt)[中文标题:]
#block(width: 150pt, stroke: 0.5pt + gray, inset: 4pt)[#t1]
#v(8pt)
#text(size: 11pt)[英文标题:]
#block(width: 150pt, stroke: 0.5pt + gray, inset: 4pt)[#t2]
#v(8pt)
#text(size: 11pt)[中英混合:]
#block(width: 150pt, stroke: 0.5pt + gray, inset: 4pt)[#t3]
