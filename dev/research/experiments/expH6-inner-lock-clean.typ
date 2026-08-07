// ============================================================
// 实验 H6: 无 show-set 污染, 验证内层 text(size:) 锁公式（U3 路径A）
// ============================================================
#set page(width: 400pt, height: 200pt, margin: 15pt)

#context {
  let w = 150pt
  // 干净基准: 9pt 与 10pt 单层公式
  let f9 = measure(text(size: 9pt)[$x^2 + y^2 = z^2$], width: w).height
  let f10 = measure(text(size: 10pt)[$x^2 + y^2 = z^2$], width: w).height
  // 外层 9pt + 内层 text(size: 10pt) 包公式
  let fA = measure(text(size: 9pt)[text(size: 10pt)[$x^2 + y^2 = z^2$]], width: w).height

  metadata((
    "test": "expH6-inner-lock-clean",
    "f9": f9,
    "f10": f10,
    "fA-inner-10pt": fA,
    "A-recovers-to-10": fA - f10,  // ≈0 → 内层锁定生效
    "A-not-scaled": fA - f9,       // >0 → 未随外层 9pt 缩放
  ))
}
