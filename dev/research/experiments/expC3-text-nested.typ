// ============================================================
// 实验 C3: 内层 text(size:) 覆盖外层缩放的普遍性验证（纯文本）
// 确认 C2 的"内层锁定无效"是普遍行为还是公式特例
// ============================================================
#set page(width: 300pt, height: 200pt, margin: 15pt)

#context {
  let t10 = measure(text(size: 10pt)[Hello]).height
  let t9 = measure(text(size: 9pt)[Hello]).height
  // 内层 10pt 在外层 9pt 内 —— 若内层生效应 = t10
  let t9in10 = measure(text(size: 9pt)[text(size: 10pt)[Hello]]).height
  // 反向: 内层 9pt 在外层 10pt 内 —— 若内层生效应 = t9
  let t10in9 = measure(text(size: 10pt)[text(size: 9pt)[Hello]]).height

  metadata((
    "test": "expC3-text-nested",
    "t10": t10,
    "t9": t9,
    "t9in10": t9in10,
    "t10in9": t10in9,
    "inner-10pt-recovers": t9in10 - t10,   // 0 = 无效; 负 = 外层仍主导
    "inner-9pt-recovers": t10in9 - t9,     // 0 = 无效; 正 = 外层仍主导
  ))
}
