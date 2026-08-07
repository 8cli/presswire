// ============================================================
// 实验 H2: show-set 规则锁定字号（U3 候选方案）
// 验证: show math.equation: set text(size: 10pt) 能否在外层
// text(size: 9pt) 缩放包裹下锁定公式字号为 10pt
// ============================================================
#set page(width: 400pt, height: 300pt, margin: 15pt)

// 锁定公式字号: show-set 规则
#show math.equation: set text(size: 10pt)

#context {
  // 基准: 10pt 公式高
  let base10 = measure(text(size: 10pt)[$x^2 + y^2 = z^2$]).height
  // 外层缩到 9pt + show-set 锁定 10pt —— 若锁定生效应 ≈ base10
  let locked = measure(text(size: 9pt)[$x^2 + y^2 = z^2$]).height
  // 对照: 无 show-set 时 9pt 公式
  let scaled = measure(text(size: 9pt)[$x^2 + y^2 = z^2$]).height

  metadata((
    "test": "expH2-showset-lock",
    "math-10pt-base": base10,
    "math-9pt-in-9pt-wrapper": scaled,
    "math-showset-10pt-in-9pt-wrapper": locked,
    "showset-recovery": locked - base10,  // ≈0 → show-set 生效
    "no-showset-scaling": scaled - base10, // ≈ -0.68 → 无锁定时随缩放
  ))
}
