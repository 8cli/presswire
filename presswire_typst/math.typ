// math.typ — 数学公式管件（任务 12，N2 + U3 定案）
//
// U3 定案（expH2/5 实测）: `show math.equation: set text(size: 10pt)` 锁公式
// 字号，免疫 autofit 外层缩放（外层 text(size:) 包裹下公式仍 10pt 高精确）。
// - 内层 text(size:) 锁公式无效（expH6: 公式元素不吃 text 直接参数）
// - set math(size:) 非法（math 是模块非元素，实测报错）
//
// 公式内容来自 plates 输入的 `$...$`（render_typst 生成 math.equation
// 表达式——字符串插值不解析 markup，须结构化构建，2026-08-08 实测）。
//
// 用法: render-doc 内 #math-setup() 应用锁字号规则（show 需函数体直接作用域）

#let math-setup() = {
  // 锁公式字号（U3: 不随 autofit 旋钮缩放）
  show math.equation: set text(size: 10pt)
  none
}
