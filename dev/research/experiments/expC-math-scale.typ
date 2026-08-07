// ============================================================
// 实验 C: 数学公式字号 × autofit 缩放（登记风险 #4, U3 关键）
// 验证: text(size:) 缩放对内联/块级公式的影响
// ============================================================
#set page(width: 300pt, height: 300pt, margin: 15pt)

#text(size: 10pt)[C1(10pt): 内联 $x^2 + y^2 = z^2$ 公式]
#v(4pt)
#text(size: 14pt)[C2(14pt): 内联 $x^2 + y^2 = z^2$ 公式]
#v(8pt)

#text(size: 10pt)[C3(10pt) 块级:]
$ x^2 + y^2 = z^2 $
#v(4pt)
#text(size: 14pt)[C4(14pt) 块级:]
$ x^2 + y^2 = z^2 $
#v(8pt)

#context {
  // 关键: 在不同 text size 下量的公式高度
  let h10 = measure(text(size: 10pt, $x^2 + y^2 = z^2$)).height
  let h14 = measure(text(size: 14pt, $x^2 + y^2 = z^2$)).height
  // 内联在 text 中
  let h-inline10 = measure(text(size: 10pt)[$x^2 + y^2 = z^2$]).height
  let h-inline14 = measure(text(size: 14pt)[$x^2 + y^2 = z^2$]).height
  metadata((
    "test": "expC-math-scale",
    "h-math-at-10pt": h10,
    "h-math-at-14pt": h14,
    "ratio-block": h14 / h10,
    "h-inline-at-10pt": h-inline10,
    "h-inline-at-14pt": h-inline14,
    "ratio-inline": h-inline14 / h-inline10,
  ))
}
