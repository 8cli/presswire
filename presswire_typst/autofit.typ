// autofit.typ — autofit-in-typst 适配层（任务 11，D3 债务消除）
//
// 核心: framefit 0.1.0 fit-copy（expE 实测）——编译内 measure 二分收敛，
// 单次 compile（对比 latin 3-16 次 xelatex 循环）。
//   fit-copy(min: ratio, max: ratio|none, max-lines, steps: 24,
//            only-if-overflow: false, body)
//   - 无 width/height 参数: layout(size => ...) 内用容器尺寸（固定版心内 =
//     block 宽高）；min/max 是比例非长度
//   - only-if-overflow: true 先测 100% 装得下则不缩放（内容不满不放大）
//   - 只缩字号**不报溢出**——溢出报告归 plate.typ 的 measure + metadata
//
// 注意（2026-08-08 集成实测）: fit-copy 内层 layout 需要宽度约束——包在
// columns 内时容器 = 列宽；包在 render-doc 版式外层时容器 = 版心宽。
// one-liner 线性初值（计划调研补充）: only-if-overflow 快速路径已覆盖
// "不满不缩"场景，24 步二分对溢出场景收敛足够——初值优化留待需要时。

#import "@preview/framefit:0.1.0": fit-copy

#let autofit-body(
  body,
  min-scale: 50%,
  max-scale: 100%,
  steps: 24,
) = {
  fit-copy(min: min-scale, max: max-scale, steps: steps, only-if-overflow: true, body)
}
