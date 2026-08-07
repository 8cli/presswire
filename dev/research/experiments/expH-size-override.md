# 实验 H — text size 覆盖规则：measure 无约束异常 + U3 定案

> 日期：2026-08-07 · Typst 0.15.1 · 源文件：expH-size-override / expH2-showset-lock / expH3-render / expH4-constrained / expH5-math-lock-final / expH6-inner-lock-clean

## 背景

文档（text 参考）说「内层 `text(size: 绝对长度)` 生效」，但早期实验 expC3 显示「外层赢」。本系列用**有约束 measure + 渲染目检**双通道复核，纠正了 expC3 的错误结论。

## 关键发现 1：measure 无约束时对嵌套 text 异常（重要陷阱！）

| 实验 | 方式 | 结果 |
|---|---|---|
| expH1 | `measure(text(size:9pt)[text(size:10pt)[Hello]]).width`（无约束） | **79.65pt**（离谱！应为 ~22pt） |
| expC3 | 同结构 `.height`（无约束） | 5.92pt（=9pt，误判外层赢） |
| expH3 | **渲染目检**（80dpi 像素分析） | 内层 10pt 生效（行高 7px = 10pt 档） |
| expH4 | `measure(..., width: 150pt)`（**有约束**） | **6.58pt = 10pt 行高，内层精确生效**（nested-vs-9 = +0.66pt） |

**结论**：`measure` **无宽度约束时对嵌套 text 元素的测量不可靠**（宽度/高度异常）；**有宽度约束（`width: W`）时完全正常**。presswire 的 framefit 与 P0 测法 C 都用宽度约束——**生产路径不受影响**。但任何无约束 measure（如测自然宽）要避免测嵌套 text。

## 关键发现 2：文本 vs 公式的字号锁定差异（U3 定案）

| 目标 | 内层 `text(size: 绝对)` 锁定 | `show ...: set text(size:)` 锁定 |
|---|---|---|
| **文本**（expH4） | ✅ 生效（10pt 内层 +0.66pt） | ✅ 生效 |
| **公式**（expH6） | ❌ **无效**（6.15pt 仍随外层 9pt） | ✅ 生效（expH2/5：6.83pt = 10pt 锁定） |

**原因**：`math.equation` 元素的字号由样式（show/set）控制，内层 `text` 元素的直接参数不能穿透公式元素。

## U3 结论（对 presswire 任务 12）

**用 show-set 规则锁定公式字号**——官方文档推荐的公式字体方式（`show math.equation: set text(font: ...)`），实测对外层缩放免疫：

```typst
#show math.equation: set text(size: 10pt)  // 锁定公式字号, 不随 autofit 旋钮
```

- 外层 framefit 的 `text(size: 1em * factor)` 缩放**不会**覆盖此锁定（expH2/5 实证）。
- 文本内容的字号锁定可用内层 `text(size:)` 或 show-set 任意一种。

## 修正 expC 的误导结论

- expC 曾推断「公式随 text(size:) 缩放 ratio 1.4，内层锁定无效」——**部分错误**：
  - 「公式随外层 text(size:) 缩放」✅ 正确（expH6 f9=6.15 vs f10=6.83 确认）。
  - 「内层 text(size:) 锁定无效」❌ 对公式成立，但对**文本**不成立（expH4）——且 expC2 的无效结论源于**无约束 measure 异常**，需弃用。
- **正确的锁定手段**：公式用 show-set（任务 12 采用）；文本内层 text 即可。

## 对 presswire 的完整建议

1. **所有 measure 一律带宽度约束**（`measure(content, width: W)`）——既符合 framefit 模式，也避开无约束嵌套异常。
2. **任务 12（math.typ）**：`show math.equation: set text(size: 10pt)` 锁公式字号，autofit 缩放不破坏公式。
3. **任务 7/17 溢出量测**：测正文（可能含用户嵌套 text 样式）时用 `measure(block(width: W, body)).height` 或 `measure(body, width: W).height`——有约束，可靠。
4. 若需测**自然宽**（任务 15 标题超宽检测），测无嵌套的纯文本可放宽约束；含嵌套样式时先渲染目检或拆解。
