# 实验 R — 固定块内 columns() 行为（任务 8 前置 spike）

> 日期：2026-08-08 · Typst 0.15.1 · 源文件：`/tmp/spike-columns/col-spike.typ`

## 问题

计划风险登记: "columns() 内容分配与溢出未文档化"——固定块（plate-frame）内
`columns(2)` 的列分配/列高/溢出行为未知。任务 8 前置 spike 验证。

## 实测（3 实验）

| 实验 | 场景 | 结果 |
|---|---|---|
| 1 | 固定块 380×150pt 内 columns(2)，30+25 句 lorem | ✅ 两栏正常分列，段落级分列正确（第二段进第二列） |
| 2 | 固定块 380×100pt 内 columns(2)，lorem(200) 超长 | ✅ 固定块含住溢出不推页（clip 生效，编译成功） |
| 3 | `measure(columns(2, gutter: 8pt)[lorem(100)], width: 380pt).height` | ✅ 自然高 215.86pt / 251.83pt 精确量出 |

## 结论

**columns() 在固定块内完全可用，无需退回 grid 方案。**
- 列分配：段落级分列，列高默认平衡（balanced 模式）。
- 溢出：columns 平衡列高到自然高 → 外层固定块 clip 含住（plate-frame 兜底）。
- 量测：`measure(columns(...), width: W).height` 可测自然高（配合任务 7 报告通道）。

## 对任务 8 的定案

- `columns.typ`（P2-P4 等宽多栏）用 `columns(n, gutter: colGap)`，包进 plate-frame。
- 侧栏（mainaside）用 `state()` 收集器（expL 定案）+ 固定块截断（任务 7 通道）。
- 列数由 `p.columns` 字段驱动（latin `\begin{storycolumns}[3]` 对应 `columns(3)`）。
