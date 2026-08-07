# 实验 G — place() 绝对定位机制（任务 13 画报排版前置）

> 日期：2026-08-07 · Typst 0.15.1 · 源文件：`expG-place.typ`（渲染证据：`expG-place-1.png` / `expG-place-hi-1.png`）

## 问题

任务 13（画报排版）计划用 `place()` 做绝对定位。需要确认 place 的坐标系、偏移、重叠行为——为画报 mini-spike 打基础。

## 实验内容（5 场景）

| 场景 | 输入 | 验证点 |
|---|---|---|
| A | `place(box(60x60)[A 左上])` | 默认定位基准 |
| B | `place(dx: 40pt, dy: 40pt, ...)` | dx/dy 偏移 |
| C | `place(right + top, ...)` | 对齐点相对定位 |
| D1/D2 | 两个重叠 box | 重叠与 z-order |
| E | `place` 在 block 内 | 相对 block 还是页面定位 |

## 结果

- ✅ 编译成功，1 页（`expG-place.pdf`）。
- 渲染 PNG 生成（80dpi，`expG-place-hi-1.png`）供目检；像素读取受限未做数值分析，但**编译 + 无报错**确认 place 基本语法/参数可用。
- 结合官方文档（typst-official-docs-study.md「place」节）已确认的语义：

| place 语义 | 官方依据 |
|---|---|
| 相对**父容器**定位（block/box/rect）；顶层 = 页面文本区 | 文档原话 |
| **含边距整页定位 → `page.foreground`/`background`** | 文档原话 |
| `dx`/`dy` 相对对齐点偏移（move 语义，不影响流布局） | 文档原话 |
| 覆盖式 `float: false` 不占流空间，但调用点插入不可见块级元素**可能断段**（包 box 规避） | 文档原话 |
| `float: true` 浮动式挤开内容；`place.flush()` 强制先排 | 文档原话 |
| **parent-scoped placement 只支持 `float: true`**（跨栏跳出） | 文档原话 |

## 待 spike 验证（文档未明确，任务 13 mini-spike 时做）

1. **layout 回调内能否 place**（画报若在 framefit 缩放范围内需确认）。
2. **grid 固定轨道内容溢出视觉行为**（grid 无 clip 参数，内容超宽会突出）。
3. **0.15 基线信息保留改动对 place 偏移的影响**（回归比对 0.14）。

## 对 presswire 的建议

- 画报整页定位**优先 `page.foreground`/`background`**（避开顶层 place 只相对文本区的限制）。
- 跨栏跳出用 `place(scope: "parent", float: true, ...)`。
- 段落内 place 包 `box` 防断段。
- 画报实现方案：`place()` 贪心装配（唯一现成参照：AGPL rjldtp 的 worst-fit 算法思路，仅借鉴思想）——任务 13 前先 mini-spike 验证贪心可行，不行降级 grid 网格布局。
