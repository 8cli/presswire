// ============================================================
// 实验 H: text size 覆盖规则复验（文档 vs 实测矛盾）
// 文档: "内层 text(size: 绝对长度) 生效"; 实测 expC3 显示外层赢
// 用宽度测量（对字号更敏感）+ show-set 锁定路径
// ============================================================
#set page(width: 400pt, height: 300pt, margin: 15pt)

// 场景 H1: 直接参数嵌套 —— 宽度对比（字号越宽越宽）
// 纯 9pt 与纯 10pt 的 "Hello" 宽度作基准
#context {
  let w9 = measure(text(size: 9pt)[Hello]).width
  let w10 = measure(text(size: 10pt)[Hello]).width
  // 外层 9pt 内层 10pt（绝对）—— 若内层生效应接近 w10
  let w9in10 = measure(text(size: 9pt)[text(size: 10pt)[Hello]]).width
  // 外层 9pt 内层 10pt（em 相对）—— em 基于外层 9pt, 10pt=1.111em
  let w9in10em = measure(text(size: 9pt)[text(size: 1.111em)[Hello]]).width

  metadata((
    "test": "expH-size-override",
    "w9": w9,
    "w10": w10,
    "w9in10": w9in10,
    "w9in10em": w9in10em,
    "inner-abs-effective": w9in10 - w10,  // ≈0 → 内层绝对生效
    "inner-abs-ineffective": w9in10 - w9, // ≈0 → 外层赢
  ))
}
