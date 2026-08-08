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
#import "theme.typ": themes, theme-state, apply-theme
#import "autofit.typ": autofit-body
#import "math.typ": math-setup
#import "poster.typ": render-poster
#import "cjk.typ": *   // 任务 14: 四包 show 规则 import 后全局生效（expQ 验证）

#let render-doc(
  plates,                        // 版数据数组（render_typst.py 生成）
  theme: "broadsheet",           // 主题预设（--theme 插槽，任务 9）
  autofit: true,                 // autofit 旋钮（--no-autofit → false，单编译纯生成）
  paper-width: 420mm,            // A3 横向（latin docopts: paper=a3,landscape）
  paper-height: 297mm,
  margin: (x: 15mm, y: 15mm),    // 版心在 plate-frame 内管理（latin padTop 20/padSide 15/bottom 16）
  plates-per-page: 1,            // 每页版数（plates=2 → 双版并排 grid，expO2 定案）
  body-size: 10pt,
  header-size: 8pt,
) = {
  let t = themes.at(theme, default: themes.at("broadsheet"))
  set page(width: paper-width, height: paper-height, margin: margin)
  set text(size: body-size, lang: "zh", region: "cn",
           font: t.at("body-font"), fill: t.at("ink"))
  set par(justify: true, leading: 0.65em)
  // 公式字号锁定（U3: 免疫 autofit 缩放）
  math-setup()
  // 主题 state 同步（atoms 内 context 读 accent/ink）
  theme-state.update(t)

  // 版心尺寸（latin linotype.cls 契约）: contentH = 297 − 20 − 16 = 261mm
  // 双版并排（plates=2）: 每版宽 = 0.5·paperW − 2·padSide（latin contentW 公式）
  // 2026-08-08 修复: 微收 2pt——词框 ink 外伸（斜体/引号）曾致左版右缘
  // 溢出 2pt 被 clip 裁剪（用户反馈）；收窄后任何 ink 外伸都在 block 内。
  let content-w = if plates-per-page == 2 {
    paper-width * 0.5 - 2 * 15mm - 2pt
  } else {
    paper-width - 2 * 15mm - 2pt
  }
  let content-h = paper-height - 20mm - 16mm
  let col-gap = 3.75mm   // latin \colGap（双版并排的栏缝）
  // ink 边距（2026-08-08）: 字形 ink 外伸贴 block 右缘被 clip 裁剪 → grid
  // 总宽收 4pt；plate-frame measure 须用同宽（width - INK-MARGIN）保证
  // fill 准确（measure 与渲染一致）。
  let INK-MARGIN = 4pt

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

  // ---- 版渲染（按 layout 分支选版式: main-aside → mainaside；其他 → columns）----
  // 单版渲染函数（autofit/日期线/plate-frame 统一组装）
  let render-one(p, idx, width) = {
    let pid = "plate-P" + str(idx)
    let layout = p.at("layout", default: "")
    let body = if layout == "main-aside" {
      render-mainaside(p, width)
    } else if layout == "poster" {
      // 画报（N3）: place 贪心装配（任务 13）——独立于 plate-frame 的
      // 版心管理（poster 内部 block 含住，plate-frame 外包 measure）
      render-poster(p, width, content-h)
    } else {
      render-columns(p, width)
    }
    // 2026-08-08 字号铁律（用户决策）: 内容不缩放，超出即信号。
    // autofit 旋钮语义重定义: 开启 = 门禁 1.0（内容超版心即 panic →
    // "文章不符合"信号）；关闭（--no-autofit）= 门禁 1.05（容忍 5% 溢出）。
    // 两者都原样渲染（不再用 framefit fit-copy——其 text() 包裹 grid 的
    // 检测在渲染时不可靠，且字号铁律下无缩放意义，2026-08-08 废弃）。
    // 2026-08-08 修复（measure 与渲染一致）: render-columns/mainaside 内部
    // grid 总宽 = content-w − INK-MARGIN(4pt)（防 ink 贴边裁剪）；plate-frame
    // 的 measure 必须用同一宽度（content-w − 4pt），否则 measure 低估高度
    // ~10pt → fill 0.99 渲染已超版心被裁（用户反馈）。
    let final-body = [#if p.at("date", default: "") != "" [
      #text(size: header-size)[#p.at("date")] \
    ]
    #body]
    plate-frame(
      final-body,
      pid,
      width: width - INK-MARGIN,
      height: content-h,
      // 2026-08-08 门禁收紧: measure 与渲染有 ~10pt 系统偏差（低估），
      // severe-fill 1.0 时 fill 0.99 渲染已超版心被裁（用户反馈）→ 收到
      // 0.97 留 3% 余量。目标 fill 区间 0.95-0.97（用户要求 ≥0.95）。
      // poster 例外: 画报固定布局（place 贪心），fill 1.0 合法 → 保持 1.05。
      severe-fill: if autofit and layout != "poster" { 0.97 } else { 1.05 },
    )
  }

  if plates-per-page == 2 {
    // ---- 双版并排（expO2 定案）: 每页 grid(1fr, 栏缝, 1fr) 两版独立固定块 ----
    for (gi, g) in plates.chunks(2).enumerate() {
      let left = g.at(0)
      let has-right = g.len() > 1
      grid(
        columns: (1fr, col-gap, 1fr),
        [#render-one(left, gi * 2 + 1, content-w)],
        [],
        if has-right {
          [#render-one(g.at(1), gi * 2 + 2, content-w)]
        } else {
          []
        },
      )
      // 非最后组才分页
      if gi < plates.chunks(2).len() - 1 {
        pagebreak()
      }
    }
  } else {
    // ---- 单版（默认）----
    for (i, p) in plates.enumerate() {
      render-one(p, i + 1, content-w)
      // 非最后版才分页（避免尾随空页）
      if i < plates.len() - 1 {
        pagebreak()
      }
    }
  }
}
