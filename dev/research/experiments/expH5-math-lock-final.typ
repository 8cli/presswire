// ============================================================
// 实验 H5: 有约束下公式字号锁定最终验证（U3 定案）
// framefit 真实模式: measure(width: W, text(size: 1em*f)[body])
// 验证两条锁定路径在内层是否生效:
//   A. 内层 text(size: 10pt) 包公式
//   B. show math.equation: set text(size: 10pt) (show-set)
// ============================================================
#show math.equation: set text(size: 10pt)

#context {
  let w = 150pt
  // 基准: 9pt 与 10pt 单层公式（有约束）
  let f9 = measure(text(size: 9pt)[$x^2 + y^2 = z^2$], width: w).height
  let f10 = measure(text(size: 10pt)[$x^2 + y^2 = z^2$], width: w).height
  // A: 外层 9pt + 内层 text(size: 10pt) 包公式
  let fA = measure(text(size: 9pt)[text(size: 10pt)[$x^2 + y^2 = z^2$]], width: w).height
  // B: 外层 9pt 包公式（show-set 已锁 10pt）
  let fB = measure(text(size: 9pt)[$x^2 + y^2 = z^2$], width: w).height

  metadata((
    "test": "expH5-math-lock-final",
    "f9": f9,
    "f10": f10,
    "fA-inner-text-lock": fA,
    "fB-showset-lock": fB,
    "A-vs-f10": fA - f10,
    "B-vs-f10": fB - f10,
    "A-vs-f9": fA - f9,
    "B-vs-f9": fB - f9,
  ))
}
