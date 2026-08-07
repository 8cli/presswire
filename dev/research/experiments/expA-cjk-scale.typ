// ============================================================
// 实验 A: autofit 字号缩放 × CJK 字体切换交互（登记风险 #2）
// 验证: text(size:) 包裹内容时, 内层 show regex 字体切换是否生效
// ============================================================
#set page(width: 300pt, height: 200pt, margin: 15pt)

// 中文字体切换规则（模拟 ctyp 的核心机制）
#show regex("[\\p{Han}，。；：！？]+"): set text(font: "Noto Serif CJK SC")

// 场景 A1: 正常缩放 1.2em —— show 规则是否随缩放仍生效?
#text(size: 12pt)[A1(12pt): 中文测试 English mixed]
#v(4pt)
#text(size: 12pt * 1.2)[A2(14.4pt): 中文测试 English mixed]
#v(4pt)
#text(size: 1.2em)[A3(1.2em): 中文测试 English mixed]
#v(8pt)

// 场景 A2: framefit 式 text(size: 1em * factor) 内嵌
#let factor = 0.9
#text(size: 1em * factor)[A4(0.9em): 中文测试 English mixed]
#v(8pt)

// 场景 A3: 检查缩放后字体是否仍为 CJK（通过 measure 行高间接验证:
// Serif CJK 与默认字体行高不同）
#context {
  let cjk-sample = text(font: "Noto Serif CJK SC")[中文测试]
  let latin-sample = text(font: "New Computer Modern")[English]
  let mixed-scaled = text(size: 1.1em)[中文 English]
  let h-cjk = measure(cjk-sample).height
  let h-latin = measure(latin-sample).height
  let h-mixed = measure(mixed-scaled).height
  metadata((
    test: "expA-cjk-scale",
    h-cjk: h-cjk,
    h-latin: h-latin,
    h-mixed: h-mixed,
    cjk-vs-latin-diff: h-cjk - h-latin,
  ))
}
