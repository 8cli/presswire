// autofit.typ — 内容-版心适配层（任务 11；2026-08-08 用户决策重定义）
//
// **用户决策（2026-08-08）: 字号固定适宜阅读，不允许缩放缩小。**
// 内容放不下 → 由 imposer 层解决（选合适长度文章 / 改写），不是缩字号。
//
// 本模块职责（autofit 模式）:
//   以固定字号（100%）渲染内容，**检测**是否超出版心——
//   - 放得下: 原样渲染（only-if-overflow 快速路径）
//   - 放不下: 报"内容超出版心（字号固定不可缩）"信号 → CLI 退出码 1 →
//     imposer 响应: 换合适长度文章 或 改写缩小（不是字号缩放）
//
// 实现: framefit 0.1.0 fit-copy（expE 实测）仅用其"检测 100% 是否装得下"
// 能力（only-if-overflow: true + min/max 都是 100% → 不缩放、只判断）:
//   - only-if-overflow: true 先测 100%，装得下 → 不缩放原样输出
//   - 装不下 → fit-copy 按 min 缩放尝试……但 min=max=100% 时无法缩 →
//     panic "content does not fit"（framefit 自身语义，成为信号）
// 注: min: 100%, max: 100% 时 framefit 行为 = 只测 100%，失败即 panic——
// 这正是"固定字号 + 超出即信号"的语义。
//
// 版本注意: framefit 0.1.0 的 min/max 是比例非长度；only-if-overflow
// 要求 min ≤ 100%。

#import "@preview/framefit:0.1.0": fit-copy

#let autofit-body(
  body,
  min-scale: 100%,   // 固定 100%: 不缩放（用户决策——字号适宜阅读优先）
  max-scale: 100%,
  steps: 24,
) = {
  fit-copy(min: min-scale, max: max-scale, steps: steps, only-if-overflow: true, body)
}
