// ============================================================
// 实验 C2: 内层 text(size:) 是否覆盖外层缩放（U3 对策验证）
// 外层 framefit 缩放到 0.9x, 内层公式固定 10pt → 公式应保持 10pt
// ============================================================
#set page(width: 300pt, height: 200pt, margin: 15pt)

#context {
  // 基准: 10pt 公式高
  let base = measure(text(size: 10pt)[$x^2 + y^2 = z^2$]).height
  // 外层缩到 0.9 (仿 framefit text(size: 1em*0.9)), 公式内层固定 10pt —— 孤立量
  let scaled = measure(text(size: 9pt)[$x^2 + y^2 = z^2$]).height
  let locked = measure(text(size: 9pt)[text(size: 10pt)[$x^2 + y^2 = z^2$]]).height

  metadata((
    "test": "expC2-nested-fix",
    "math-base-10pt-h": base,
    "math-scaled-9pt-h": scaled,
    "math-locked-inside-9pt-h": locked,
    "outer-scaling-effect": scaled - base,
    "inner-lock-recovery": locked - base,
  ))
}
