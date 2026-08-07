// ============================================================
// 实验 O2: plates=2 双版并排机制（任务 16 契约）
// linotype: 每页两个 plate 盒并排 (P1|P2, P3|P4), 各自独立固定版心
// ============================================================
#set page(width: 420pt, height: 297pt, margin: 15pt)

// 每个 plate 是固定版心块, 两两并排
#grid(
  columns: (1fr, 10pt, 1fr),
  gutter: 0pt,
  [#block(
    width: 100%, height: 250pt, clip: true, breakable: false,
    stroke: 0.5pt + rgb("#888"), inset: 8pt,
  )[#text(size: 9pt)[#lorem(60)] #label("plate-P1")]],
  [],
  [#block(
    width: 100%, height: 250pt, clip: true, breakable: false,
    stroke: 0.5pt + blue, inset: 8pt,
  )[#text(size: 9pt)[#lorem(80)] #label("plate-P2")]],
)

// 每版独立 metadata 报告
#context {
  let h1 = measure(block(width: 100%, lorem(60)), width: 195pt).height
  let h2 = measure(block(width: 100%, lorem(80)), width: 195pt).height
  metadata((
    "test": "expO2-side-by-side",
    "P1-natural-h": h1,
    "P2-natural-h": h2,
    "frame-h": 250pt,
    "P1-overflow": h1 > 250pt,
    "P2-overflow": h2 > 250pt,
    "pages": counter(page).get().last(),
  ))
}
