// ============================================================
// 实验 H4: 有宽度约束下 measure 嵌套 text（framefit 真实场景）
// framefit 用 measure(width: size.width, text(size: 1em*f)[body])
// body 含用户嵌套 text（强调/字号）—— measure 是否可靠？
// ============================================================
#set page(width: 400pt, height: 300pt, margin: 15pt)

#context {
  // 基准: 纯文本 9pt 与 10pt 在 150pt 约束下的高度
  let h9 = measure(text(size: 9pt)[Hello world hello world], width: 150pt).height
  let h10 = measure(text(size: 10pt)[Hello world hello world], width: 150pt).height
  // 嵌套: 外层 9pt + 内层 10pt 片段
  let hnested = measure(text(size: 9pt)[Hello world #text(size: 10pt)[BIG] hello world], width: 150pt).height
  // 嵌套对照: 外层 10pt + 内层 9pt
  let hnested2 = measure(text(size: 10pt)[Hello world #text(size: 9pt)[small] hello world], width: 150pt).height
  // 纯渲染参考（无 measure, 直接放文档里）

  metadata((
    "test": "expH4-constrained",
    "h9-150w": h9,
    "h10-150w": h10,
    "hnested-9w10-inner": hnested,
    "hnested2-10w9-inner": hnested2,
    "nested-vs-9": hnested - h9,     // >0 → 内层 BIG 生效（高一点）
    "nested2-vs-10": hnested2 - h10, // <0 → 内层 small 生效（矮一点）
  ))
}
