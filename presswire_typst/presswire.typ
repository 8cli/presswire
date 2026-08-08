// presswire.typ — presswire 主模板（任务 5 初版：page + 逐版占位排版）
//
// 演进计划:
//   任务 7  plate.typ    固定版心 + measure + metadata 溢出报告 ✅（已接入）
//   任务 8  mainaside.typ/columns.typ  版式（main-aside / 等宽多栏）
//   任务 9  theme.typ    主题预设（broadsheet/magazine）
//   任务 10 atoms.typ    原子（kick/headline/deck/photo/...）markup 富文本渲染
//   任务 12 math.typ     数学公式管件
//   任务 13 poster.typ   画报版型
//   任务 16 cli 接入     参数化 paper/margin/template 路径
//
// 本版职责: page 设置 + 逐版渲染（经 plate-frame 固定版心 + 溢出报告）。
//
// 语法注意: 函数体 `= { }` 是 code mode——顶层 set/if/for 不带 `#`；
// content 块 `[...]` 内的表达式（#text/#if/#for/#v）才带 `#`。

#import "plate.typ": plate-frame
#import "mainaside.typ": render-mainaside
#import "columns.typ": render-columns

#let render-doc(
  plates,                        // 版数据数组（render_typst.py 生成）
  paper-width: 420mm,            // A3 横向（latin docopts: paper=a3,landscape）
  paper-height: 297mm,
  margin: (x: 15mm, y: 15mm),    // 版心在 plate-frame 内管理（latin padTop 20/padSide 15/bottom 16）
  body-size: 10pt,
  header-size: 8pt,
) = {
  set page(width: paper-width, height: paper-height, margin: margin)
  set text(size: body-size, lang: "zh", region: "cn",
           font: ("Noto Serif CJK SC", "Noto Sans CJK SC",
                  "Libertinus Serif", "New Computer Modern"))
  set par(justify: true, leading: 0.65em)

  // 版心尺寸（latin linotype.cls 契约）: contentH = 297 − 20 − 16 = 261mm
  let content-w = paper-width - 2 * 15mm
  let content-h = paper-height - 20mm - 16mm

  // ---- 空版占位嵌入（无 plates 输入时仍能编译出 PDF）----
  if plates.len() == 0 {
    align(center)[
      #text(size: 24pt, weight: "bold")[空版占位]
      #v(8pt)
      #text(size: 11pt)[presswire 初版模板 — 未提供 plates 输入]
      #v(4pt)
      #text(size: 9pt)[（任务 7: 固定版心 + 溢出报告已接入）]
    ]
    return
  }

  // ---- 逐版排版（按 layout 分支选版式: main-aside → mainaside；其他 → columns）----
  for (i, p) in plates.enumerate() {
    let pid = "plate-P" + str(i + 1)
    let layout = p.at("layout", default: "")
    let body = if layout == "main-aside" {
      render-mainaside(p, content-w)
    } else {
      render-columns(p, content-w)
    }
    plate-frame(
      // 日期线（版顶，latin \dateline 计入版心预算）
      [#if p.at("date", default: "") != "" [
        #text(size: header-size)[#p.at("date")] \
      ]
      #body],
      pid,
      width: content-w,
      height: content-h,
    )
    // 非最后版才分页（避免尾随空页）
    if i < plates.len() - 1 {
      pagebreak()
    }
  }
}
