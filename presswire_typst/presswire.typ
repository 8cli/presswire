// presswire.typ — presswire 主模板（任务 5 初版：page + 逐版占位排版）
//
// 演进计划:
//   任务 7  plate.typ    固定版心 + measure + metadata 溢出报告（替换下方占位 block）
//   任务 8  mainaside.typ/columns.typ  版式（main-aside / 等宽多栏）
//   任务 9  theme.typ    主题预设（broadsheet/magazine）
//   任务 10 atoms.typ    原子（kick/headline/deck/photo/...）markup 富文本渲染
//   任务 12 math.typ     数学公式管件
//   任务 13 poster.typ   画报版型
//   任务 16 cli 接入     参数化 paper/margin/template 路径
//
// 本版职责: page 设置 + 逐版占位渲染 + 空版占位嵌入（验收: 空版能 compile 出 PDF）。
//
// 语法注意: 函数体 `= { }` 是 code mode——顶层 set/if/for 不带 `#`；
// content 块 `[...]` 内的表达式（#text/#if/#for/#v）才带 `#`。

#let render-doc(
  plates,                        // 版数据数组（render_typst.py 生成）
  paper-width: 420mm,            // A3 横向（latin docopts: paper=a3,landscape）
  paper-height: 297mm,
  margin: (x: 20mm, y: 15mm),
  body-size: 10pt,
  header-size: 8pt,
) = {
  set page(width: paper-width, height: paper-height, margin: margin)
  set text(size: body-size, lang: "zh", region: "cn",
           font: ("Noto Serif CJK SC", "Noto Sans CJK SC",
                  "Libertinus Serif", "New Computer Modern"))
  set par(justify: true, leading: 0.65em)

  // ---- 空版占位嵌入（无 plates 输入时仍能编译出 PDF）----
  if plates.len() == 0 {
    align(center)[
      #text(size: 24pt, weight: "bold")[空版占位]
      #v(8pt)
      #text(size: 11pt)[presswire 初版模板 — 未提供 plates 输入]
      #v(4pt)
      #text(size: 9pt)[（任务 7 将在此替换为固定版心 + 溢出报告）]
    ]
    return
  }

  // ---- 逐版排版（占位实现: 任务 7 换 plate.typ 固定版心）----
  for (i, p) in plates.enumerate() {
    block(width: 100%, stroke: 0.5pt + gray, inset: (x: 10pt, y: 8pt))[
      // 版头字段
      #if p.at("date", default: "") != "" [
        #text(size: header-size)[#p.at("date")] \
      ]
      #if p.at("kicker", default: "") != "" [
        #text(size: 9pt, weight: "bold")[#p.at("kicker")] \
      ]
      #if p.at("headline", default: "") != "" [
        #text(size: 15pt, weight: "bold")[#p.at("headline")] \
      ]
      #if p.at("subheadline", default: "") != "" [
        #text(size: 11pt, weight: "bold")[#p.at("subheadline")] \
      ]
      #if p.at("deck", default: "") != "" [
        #text(size: body-size, style: "italic")[#p.at("deck")] \
      ]
      #if p.at("byline", default: "") != "" [
        #text(size: header-size)[#p.at("byline")] \
      ]
      #if p.at("expanded", default: "") != "" [
        #text(size: body-size + 1pt, weight: "bold")[#p.at("expanded")] \
      ]
      // 正文
      #for para in p.at("body", default: ()) [
        #par[#para]
      ]
      // 引文
      #if p.at("pullquote", default: "") != "" [
        #v(4pt)
        #block(stroke: (left: 2pt + black), inset: (left: 6pt), width: 100%)[
          #text(size: body-size + 1pt, style: "italic")[#p.at("pullquote")]
        ]
      ]
      // 副故事
      #for st in p.at("stories", default: ()) [
        #v(4pt)
        #text(size: 11pt, weight: "bold")[#st.at("headline", default: "")]
        #if st.at("byline", default: "") != "" [
          #text(size: header-size)[#st.at("byline")] \
        ]
        #for para in st.at("body", default: ()) [
          #par[#para]
        ]
      ]
      // 简讯
      #if p.at("briefs", default: ()).len() > 0 [
        #v(4pt)
        #text(size: 9pt, weight: "bold")[IN BRIEF] \
        #for item in p.at("briefs", default: ()) [
          #item \
        ]
      ]
      #if p.at("mainbriefs", default: ()).len() > 0 [
        #v(4pt)
        #text(size: 9pt, weight: "bold")[MAIN BRIEFS] \
        #for item in p.at("mainbriefs", default: ()) [
          #item \
        ]
      ]
    ]
    pagebreak()
  }
}
