# Typst 官方文档研究 — presswire 核心机制

> 日期：2026-08-07 · 来源：typst.app/docs 官方参考（WebFetch 直抓）+ 本地 0.15.1 实证交叉验证
> 目的：完整理解 presswire 依赖的 Typst 核心机制，避免设计踩坑

## 一、核心哲学（文档原话提炼）

1. **值语义**：content/长度/字典/数组都是可编程值，元素可存储、可程序处理。
2. **纯函数 + 上下文边界**：`measure`/`query`/`counter.get` 等是 **contextual** 函数——「Contextual functions can only be used when the context is known」。普通代码不感知文档位置。
3. **多遍编译**：「To resolve all your queries, Typst evaluates and layouts parts of the document multiple times」「document did not converge within five attempts」——查询/状态类功能触发多遍求值，不收敛时警告。
4. **context 可嵌套**：「Context blocks can be nested. Contextual code will then always access the innermost context.」且 context 表达式可能被求值 0/1/多次（「may be evaluated zero, one, or multiple times」）。
5. **show/set 声明式 vs context/state 命令式**：show 规则作用到当前块/文件结束；transformational show 内的 set 规则不可再被覆盖。

## 二、机制详解（文档 + 实证）

### measure
- contextual；`width: auto` = 无限可用宽度；`height: auto` = 无限高。
- 返回 `(width, height)` 字典，均为 length。
- width/height 参数 = **可用区域约束**，非 wrapper box（「the former will get the dimensions of the inner content instead of the dimensions of the block」）。
- ⚠️ **实证**：无宽度约束时 measure 对**嵌套 text 元素**异常（宽度离谱/高度误判）；**有宽度约束时完全正常**（expH 系列）。→ presswire 一律带 `width: W`。
- 「The same content can have a different size depending on the context」——measure 结果依赖上下文。

### layout
- `layout(func)` → func 收到外层容器尺寸 `(width, height)`；页内 = 页面减边距。
- 回调**自动提供 context**（「This is why `measure` can be called in the example below」）——framefit 模式的根基。
- **「forces its contents into a block-level container」且「placement relative to the page or pagebreaks are not possible within it」**——layout 回调内不能页面级定位/分页（画报整页定位须用 page.foreground/background）。
- 每次内容出现调用一次。

### context
- 需要 context 的：读 set 规则值（`text.size`/`text.lang`）、`counter.get/at`、`here()`、`query`、`1em.to-absolute()`。
- show 规则隐式提供 style context；只有 locatable 元素的 show 规则提供 location context。
- **context 表达式是 opaque**：存下来不能直接检查，放置时才解析。
- ⚠️ 含 set 规则的代码块返回 content 而非末表达式值（实证）——用 `text(size:, content)` 包裹代替。

### query / metadata / label
- `query(target)`：target 接受 label/selector/location/element function；**只支持 locatable 元素函数**（`query(label)` 本身非法——label 不是元素函数）。
- 返回元素数组；元素带 `label` 字段（有 label 时）。
- **非 locatable 元素有 label 也能被 query 找到**——metadata 正是（实证 `query(<meta-P1>)` 返回 value）。
- **⚠️ 性能**：query 触发文档多次布局求值；**自影响查询可能不收敛**（「Typst simply gives up after a few attempts」）。→ 任务 17 Python 侧跑 eval 时控制查询量，避免查询影响自身布局。
- metadata：`metadata(any)` 接受任意值；label 相邻放置关联；JSON 序列化长度字段为**字符串**（实证「"992.22pt"」）。
- `location()` → `.page()` 返回**真实物理页码**（从 1 起）；`counter(page).at(loc)` 取页计数器值；`math.equation` 是可定位元素。

### block
- width/height 可 set；固定高度超页时 **breakable: true = 按剩余高度拆分续排**（「the block will continue on the next page with the remaining height」）；breakable: false = 整块跳页。
- clip：「Whether to clip the content inside the block」——只管可见性，不影响 measure。
- above/below/spacing/sticky；sticky 默认挂 heading 防孤标题。
- **与 linotype 关键差异**：固定高度块 breakable: true 会**跨页续排**（expF 补全：页 1 放得下时自然不跨页）；presswire 用 breakable: false 显式不拆。

### show / set
- 选择器：元素函数 / `heading.where(level:)` / `<label>` / 字符串 / `regex(...)`。
- show-set 规则是最基础形式（`show regex(...): set text(font:)` 合法组合）。
- 「set rules within a transformational show rule would not be overridable anymore」。
- **字号覆盖（实证定案）**：内层 `text(size: 绝对)` 对文本生效（expH4 有约束）；**对公式不生效**（expH6）；**show-set 锁定对两者都生效且免疫外层缩放**（expH2/5）——U3 正解。

### place
- 相对**父容器**定位（block/box/rect）；顶层 = 页面文本区；**含边距整页定位放 page.foreground/background**。
- float: false = 覆盖式：盖在先前内容上，不占流空间，但调用点**插入不可见块级元素可能断段**（包 box 规避）。
- float: true = 浮动式：挤开内容；`place.flush()` 强制先排浮动元素。
- dx/dy 是位移（move 语义），不影响流布局。
- **parent-scoped placement 只支持 float: true**（跨栏）。
- ⚠️ layout 回调内能否 place 未文档化——画报 mini-spike 需验证。

### grid
- `1fr` = 剩余空间按分数分配；固定/相对长度轨道精确尺寸；auto 轨道适配内容（空间不足时均分）。
- cells 行优先填充；`grid.cell` 可指定 x/y；gutter/column-gutter/row-gutter（不是 gap）。
- 固定轨道内容溢出行为未文档化——画报 spike 验证。

### columns（⚠️ 关键限制）
- **「It will currently not balance the height of the columns」**——不均衡列高！
- 列高 = 容器高或页面剩余高；用 `colbreak` 显式换栏。
- 固定高度块内 columns 用块高（恰好符合报纸"栏目填满版心"？但**内容分配到各栏的顺序与溢出未文档化**——任务 8 需 spike）。
- 页面级分栏用 `page(columns: N)`（保 footnote/分页/行号）。

### text（CJK 宝藏）
- `size`：1em = 当前字号；em 相对前一字号；绝对长度即生效字号。
- `font`：字符串或**描述符字典**——`(name: "Inria Serif", covers: "latin-in-cjk")`！**原生 covers 分字体**（比 ctyp 正则 hack 更原生，任务 14 候选）。
- `fallback: true` 允许字体 fallback。
- **`cjk-latin-spacing`**：CJK 与拉丁字符间自动间距（auto/none）——中英混排核心参数。
- `script: auto` 按 Unicode 脚本自动选 OpenType script；`lang` 影响断词/引号。

### math
- math 是**模块**（非元素）；公式元素是 `math.equation`；`set math(...)` **非法**（实证）。
- 官方推荐公式字体：`#show math.equation: set text(font: "Pennstander Math")`——**show-set 是官方公式配置方式**。
- 块级公式判定：公式首尾各至少一个空格（`$ x^2 $`）。
- `math.equation` 是 locatable 元素。

### page
- `page(columns: N)` 页面级分栏；`width/height/margin`（auto 边距 = 2.5/21 × 较小边）。
- `background`/`foreground`：覆盖整页，相对长度按含 bleed 的页面尺寸解析；**对 AT 不可见**。
- `numbering` 用逻辑 counter 值（非物理页）。

## 三、对 presswire 的机制级建议

| presswire 模块 | 采用机制 | 依据 |
|---|---|---|
| 任务 7 plate.typ | `block(width,height,clip:true,breakable:false)` + `measure(body, width: W).height` + `#metadata #label` + Python `typst eval 'query(metadata)'` | P0 + expB + 文档（query 带 label 字段） |
| 任务 8 columns.typ | 优先 `page(columns:)` 或固定块内 columns + colbreak；**spike 列分配/溢出** | 文档「not balance」 |
| 任务 11 autofit | framefit `layout(size => measure(width: size.width, text(size: 1em*f)))` | 文档 layout 回调自动 context + expE |
| 任务 12 math.typ | `#show math.equation: set text(size: 10pt)` 锁公式字号 | expH2/5 定案 |
| 任务 13 poster.typ | `place` 相对 block + `page.foreground/background` 整页定位；spike 嵌套 layout 内 place | 文档 + 调研 |
| 任务 14 cjk.typ | 原生 `font: (name:, covers: "latin-in-cjk")` + `cjk-latin-spacing` 候选；ctyp 作 fallback | text 文档 |
| 任务 15 标题宽 | 无约束 measure 测纯文本自然宽（避免嵌套） | expH |
| 任务 17 overflow | `typst eval 'query(metadata)'` 批量 + 控制查询量（防多遍求值膨胀） | 文档 query 性能警告 |

## 四、待 spike 验证项（文档未明确）

1. columns() 在固定高度块内的**内容分配顺序与溢出行为**（任务 8）。
2. layout 回调内能否 place（画报任务 13）。
3. grid 固定轨道内容溢出视觉行为（画报）。
4. 多遍编译对 presswire 大文档（4 版 × 多 label metadata）的性能影响（任务 17 前）。
