# 实验 L — state() 收集器模式验证（任务 8 mainaside 侧栏）

> 日期：2026-08-07 · Typst 0.15.1 · 源文件：`/tmp/typst-r2/state-collector.typ`

## 问题

任务 8（mainaside 版式：主栏 2 列 + 侧栏 1 列）计划以「`state("articles")` 收集器」为起点（dashing-dept-news 官方模板模式）。需验证：state 收集器在 0.15.1 是否可用、多遍编译下是否稳定、收集内容能否按需截断（对应 linotype vsplit 语义）。

## 实测结果

构造收集器模式：`state("articles", ()).update(prev => prev + (entry,))` 在文章渲染时收集，文末侧栏 `state("articles", ()).get()` 读取渲染。

- ✅ 编译成功（1 页）。
- ✅ **收集成功**：`metadata(("collected": state(...).get().len()))` → **2**（两篇文章都收集到）。
- ✅ **侧栏渲染正确**：pdftotext 显示侧栏区「侧栏收集结果」「头条一」「头条二」标题——收集的内容在**文末（侧栏位置）正确渲染**。

## 结论

✅ **state 收集器模式在 0.15.1 完全可用**——从正文任意位置收集文章到侧栏的机制成立。任务 8 可放心采用。

## 对 presswire 任务 8 的建议

1. **收集器骨架**：`#let collect(entry) = state("articles", ()).update(prev => prev + (entry,))`；侧栏渲染时 `state("articles", ()).get()`。
2. **收集内容截断**（linotype vsplit 语义）：linotype 对超高侧栏 vsplit 截断丢弃；Typst 侧栏若超高需在渲染时 measure 对比 → clip 或缩小字号（**任务 7 的 measure 通道复用**）。state 收集的是 content，可在渲染侧栏时统一处理。
3. **多遍编译**：state 更新是声明式的，Typst 自动多遍求值收敛——本实验未触发不收敛警告；但**侧栏内容若依赖自身长度**（如截断决策影响收集），可能不收敛（对应文档"自影响查询 5 次放弃"警告）——侧栏截断决策放 Python 侧（任务 17 的 eval 读 fill 后二次调整）规避。
4. **P1 main-aside 的版式**：mainstory/asidestory 分别收集到两个 state（或一个 state 带 type 字段），渲染时 main 区 + aside 区各取所需。

## 待 spike（任务 8 起步时）

- 侧栏超高时的 measure 对比 + clip/缩字号方案（复用任务 7 通道）。
- 多版（plates=2 每页两版）时 state 作用域——是否需要每版独立 state id。
