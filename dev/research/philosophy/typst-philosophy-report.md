# Typst 哲学与开发算法研究（presswire 避坑指南）

> 日期：2026-08-07 · 证据：官方文档（WebFetch 直抓）+ 本机 typst 0.15.1 实测 + #7779 + typst-cli 源码
> 标注 [实测] 的均为 0.15.1 真实运行结果。与 `typst-official-docs-study.md`（本地实证）互为补充。

## 一、核心哲学（5 条）

1. **值语义，无宏展开**：content、长度、字典、数组都是可编程值，元素可存入变量/字典被程序处理。含义：presswire 可数据驱动排版，排版结果还可被 `query()` 反查成结构化数据——这是溢出报告的技术根基。
2. **纯函数 + 上下文边界**：普通代码不感知自己在文档中的位置（"Typst code isn't directly aware of its location in the document"），只有 `context` 表达式、`layout()` 回调、可定位元素的 show 规则内才有位置上下文。含义：`measure`/`counter.get`/`query` 一律要包进 context。
3. **多遍编译**：编译器多次处理文档以解析上下文交互（计数器/状态/查询），不收敛会警告；0.15 起有"详细诊断"定位不收敛原因。含义：presswire"单次编译收敛"依赖此机制，任何反馈回路都要警惕不收敛。
4. **set/show 声明式 vs context/state 命令式**：show 规则内嵌套的 set 规则不再可被后续覆盖（文档原话 "set rules within a transformational show rule would not be overridable anymore"），建议拆成独立 show-set 规则。含义：autofit 缩放用声明式注入，溢出检测用命令式输出。
5. **桌面排版模型**：`layout()` 回调拿容器尺寸，`measure()` 测量——天然适合固定版心；但 `layout` 强制 block 级容器，"不能在其中做页面相对放置或分页符"。

## 二、核心机制

**measure / layout / context**
- `measure(content, width: auto, height: auto)` 返回 dict（`width`/`height`，length 类型）。`auto` = 无限宽/高；`width` 参数是显式约束。
- 只能在 context 内用；`layout(size => ...)` 回调自带 context，可直接 measure。**framefit 模式**：`#layout(size => measure(width: size.width, body))`——`size.width` 就是外层容器宽度 [实测：200pt 页面带 10pt 边距 → `size.width = 180pt`]。
- **a) measure 溢出宽度（#7779 现状）**：[实测] 不可断行长词 `measure(width: 30pt, "AAA…")` → 返回 **30pt**（裁剪后），而其自然宽度 389.9pt（无约束测的）。issue #7779 仍 open、无 assignee、未修复。**好消息**：可换行内容在约束宽度下 height 是正确的（lorem 30pt 宽 → 410.1pt 高）。**坏消息**：不可断行内容在约束下 height 返回**单行高度**（7.24pt）——假阴性。
- 嵌套 layout 回调可用，但每次出现都会重跑回调；`layout` 内不能页面级放置/分页。

**query / eval / metadata / label**
- `query(target)` 返回匹配元素数组（仅可定位元素），`.location()` 拿位置，`counter(page).at(loc)` 拿页码。0.14 起 par/table/enum/list/emph/strong 等大量元素可定位（text 本身不可定位 [实测]）。
- **label 只能在 markup 模式挂** [实测]。`#context { metadata(...) } <m>` 会把 label 挂到 **context 元素**上（`query(<m>)` 返回 `{"func":"context"}`，无 `.value`）——正确姿势：`#context [ #metadata((…)) <m> ]` 或直接 `#metadata((…)) <m>`。
- **b) metadata JSON 序列化**：[实测] `30pt` → **`"30pt"` 字符串**（length 一律带单位字符串，如 measure 结果 `"410.1pt"`）；int/bool 为数字；dict→对象、array→数组。注意：metadata 存的是值本身；若值被 `context` 包裹则存成元素树（`{"func":"context"}`）。
- **e) typst eval 正确用法**：`typst query` 已弃用且从命令列表隐藏（源码 `#[command(hide = true)]` + "deprecated, use eval instead"；实测编译时打印警告）。`typst eval '<表达式>' --in doc.typ`：先完整编译文档，再在 code 模式求值表达式（有权访问 introspector），默认 `--format json`，`--format raw` 仅支持 string/bytes [源码实测]。范例：`typst eval 'query(<m>).first().value' --in doc.typ`。

**block / box**
- 参数：width/height/breakable/clip/above/below/sticky 全可 set。`clip` 只隐藏溢出不参与 measure。`spacing` 是 above/below 简写；0.12 起段落间距用 `par.spacing`。
- **breakable × 固定高度** [实测 60pt 页面放 100pt 块]：`breakable: true` → 块跨页切分（3 页）；`false` → 整块跳到下一页（2 页，前一页留白）。presswire 固定版心必须显式 `breakable: false` 并预先保证放得下，否则会莫名空页。
- `sticky` 默认挂在 heading 上（防孤标题），0.13 修复了容器顶部失效的 bug。

**show / set**
- 匹配：element 函数、`heading.where(level:1)`、`<label>`、`show "文本"`、`show regex(...)`。[实测] `\p{Han}` Unicode 属性正则**可用**（`show regex("[\p{Han}]+")` 正确匹配三处中文）。
- **c) text(size:) × show-regex 字体切换**：[实测] 外层 `#text(size: 7pt)[中文B]` 时，show-regex 规则（`set text(font: …)`）匹配到的内容 `context text.size` 报告 **7pt**——font 与 size 是独立 set 字段，字号缩放**穿透**字体切换，autofit×CJK 兼容成立。`context text.size` 返回解析后绝对值。
- 0.13 移除 `style()` 函数和 `measure` 的 `styles` 参数——老 autofit 传 styles 技巧已死，改 layout+context。

**place / grid / columns（画报相关）**
- `place(alignment, dx, dy, scope: "column"/"parent", float)`：相对父容器（block/box/rect）定位，dx/dy 相对对齐点偏移；**顶层 place 相对版心文本区**，要含边距的整页定位须放 `page.foreground/background`。非浮动 place 覆盖式不占流，但插入不可见块级元素可能断段（段落中包 box）。跳出分栏：`place(scope: "parent", float: true, top + center, …)`。
- `grid(columns: (60pt, 1fr, 2fr))`：fr 是"其余空间按比例分配"；固定列不收缩——内容超宽会**溢出突出**（grid 无 clip 参数，默认不裁剪）。auto 列"至多占剩余空间"。
- `columns()`：**文档明说当前不均衡各栏**，跨栏必须 `colbreak()`；页面级分栏用 `set page(columns:)`（保 footnote/分页/行号），容器内才用 `columns()`。

## 三、开发算法模式

- **autofit 二分（framefit 模式）**：`layout(size => …measure(width: size.width, text(size: factor * 1em)[…]).height…)` 二分收敛。注意：**`1em` 是当前字号**，二分时写成 `text(size: 1em * f)` 保证缩放基准正确；不要 em 叠 em（嵌套 `text(1.5em)` 以外层为基准 [文档+实测]）。单调性成立，但不可断行长词会假阴性 → **双测法**：①无约束 `measure(text)` 得自然单行宽 W；②有约束 `measure(width: W₀, text)` 得包裹高 H。若 W > W₀ 且 H 显示单行 → 不可断行溢出，直接判 overflow 继续缩或上报。初始值用"目标字数×经验系数"线性估计（one-liner）合理——只省迭代步数，不改变收敛性质，建议保留。
- **性能**：[实测] 50 篇 × 24 步 = 1200 次 measure 只让编译从 0.666s → 0.695s（+4%），0.12 起布局多线程化——24 步二分完全可接受。`layout()` 回调每次内容出现都执行；大文档主要成本是多遍编译（上下文不收敛时膨胀）。
- **溢出检测**：metadata+label+query 可行（`typst eval` 读 JSON），但=整文档编译一遍 + 求值一遍；**锚点页差法（edwinhu）只对跨页位移敏感，固定版心帧内溢出不改变页码 → 检测不到，不可用**。帧内溢出 = measure 高 vs 帧高对比 + 长词矛盾检测。0.15 布局不收敛会有详细诊断输出，正好当 CI 报警器。
- **CJK**：`\p{Han}` 正则可用 [实测]；show-regex set font 与 text(size:) 兼容 [实测]；`text.cjk-latin-spacing` 是 set 参数（0.15 修复了两端对齐下 CJK-Latin 间距不均）；字体列表按字形回退，`covers: "latin-in-cjk"` 描述符可精确路由（0.15 修复了 `context text.font` 的 covers 反射）；**标点悬挂/压缩无原生支持**——依赖字体 OpenType 特性，需 spike。
- **数学**：[实测] `text(size: 7pt)[$x+1$]` 高度 7.51→4.78pt（**行内公式随 text(size:) 缩放**）；`set math(size: 2em)` 对行内公式**无效**（仍 7.51pt），对独立公式有效（23.54→43.98pt）。→ 行内公式缩放一律走 `text(size:)`。（注：presswire 实证补充——`show math.equation: set text(size:)` 可锁公式字号免疫外层缩放，见 expH 系列）
- **溢出可测可报**：见"溢出检测"；另外 0.13 起 proper paragraph 区分，`par[...]` 非纯行内内容有警告——别用 par 当容器。

## 四、已知坑清单

| # | 坑（现象/触发/规避） | 相关度 |
|---|---|---|
| 1 | **measure 溢出宽度被裁剪**（#7779，open）：约束宽下不可断内容返回约束宽而非自然宽。规避：无约束测一次拿自然宽。 | 高 |
| 2 | **不可断长词假阴性**：约束宽下 height 报单行高，autofit 误判"放得下"。规避：双测矛盾检测。 | 高 |
| 3 | **layout 回调内不能页面级放置/分页**。规避：页面锚定内容放 page.foreground/background。 | 高 |
| 4 | **固定高块 breakable:false 跳页留白**。规避：帧统一 breakable:false + 帧高预算校验。 | 高 |
| 5 | **行内公式 `set math(size:)` 无效**。规避：text(size:)（presswire 定案：show-set 锁公式字号）。 | 高 |
| 6 | **label 只能 markup 挂**，context 包装会挂到 context 元素（`query(<m>).first().value` 报无 value）。规避：`#metadata(…) <m>` 相邻。 | 中 |
| 7 | **metadata 值被 context 包成元素树**（`{"func":"context"}`）无法读出。规避：context 外组装 dict。 | 中 |
| 8 | **transform show 内 set 不可再覆盖**。规避：独立 show-set 规则。 | 中 |
| 9 | **typst query 弃用**（已隐藏）。规避：typst eval（默认 JSON，raw 仅 string/bytes）。 | 中 |
| 10 | **columns() 不均衡** + 跨栏需 colbreak。规避：页面级 `set page(columns:)`。 | 中 |
| 11 | **grid 固定列溢出突出不裁剪**（无 clip 参数）。规避：列内自行包 block(width:…, clip:…) 并接受溢出可视化风险，spike 确认。 | 中 |
| 12 | **em 叠 em 基准漂移**：嵌套 text(1.5em) 相对父字号。规避：autofit 用绝对/单一 em 基准。 | 中 |
| 13 | **0.13 移除 `style()`/`measure(styles:)`**：老 autofit 示例全部失效。 | 中 |
| 14 | **0.15 基线信息保留（breaking）**：box/block 文本基线对齐改变 → 固定帧内文本垂直位置可能与 0.11 有 silent shift。规避：回归比对。 | 中 |
| 15 | **0.15 路径禁用反斜杠**（Windows 路径）。 | 低 |
| 16 | **0.15 变体字体族名自动去 "Variable" 后缀**；`text.features` 解析更严。 | 低 |
| 17 | **0.15 `lr` size 相对内高而非定界符**、glyph 拉伸相对基字——数学公式尺寸可能与旧版不同。 | 低 |

## 五、版本注意（0.11→0.15）

- **0.12**：段落间距 `par.spacing` 取代 `show par: set block(spacing:)`；`measure` 新增 width/height 参数；布局多线程（2-3 倍）；`place.scope`/`figure.scope`、`block.sticky`、`place.flush`；弃用 `style`/`locate(回调)`/`query(+loc)`/`counter.display`/`state.display`。
- **0.13**：proper paragraph（`par` show 规则语义收窄）；移除 `style`、`measure(styles:)`、`state.display`、`query(location:)`、`locate` 兼容行为；`image.path→source`；`path`→`curve`（path 弃用→0.15 移除）；outline 重构。
- **0.14**：大批元素可定位；`typst info`/`completions`；`--deps` 取代 `--make-deps`；空 label 报错；`int=="integer"` 兼容移除。
- **0.15**：**基线信息保留（breaking，box/block 对齐变化）**；`pattern→tiling`、`pdf.embed→pdf.attach` 移除；路径反斜杠禁用；`--timings` 需显式文件名；新增 `within` selector；布局不收敛详细诊断；CJK-Latin 间距修复；SimSun-ExtB 字体例外。
- **universe 包**：包与编译器强耦合（API 随版本演进），0.15 需选配已适配 0.15 的包版本；具体包（如 CWT 系）上线前逐一 `typst compile` 冒烟。

## 六、对 presswire 的直接建议

**值得采用的模式**
1. framefit 双测 autofit：`layout(size => …)` 传帧宽 → `measure(width: size.width, text(size: f*1em)[…])`，24 步二分（实测开销可忽略），初值用线性估计。
2. metadata + `typst eval` JSON 溢出报告；记得把 JSON 里的 length 字符串（"410.1pt"）按数字解析。
3. `\p{Han}` 正则字体路由 + `text(size:)` 缩放穿透验证通过——autofit 与 CJK 混排可组合。
4. 数学公式统一 show-set 锁字号（presswire expH 定案）或 text(size:) 缩放（行内/独立都有效）。

**要提前防的坑**
- 长词不可断 → 双测矛盾检测；溢出报告保留原文与帧 id，让上层可二次干预。
- 帧容器统一 `breakable: false`，帧高预算校验（防跳页空白）。
- 帧内溢出检测**不能用**锚点页差法；用 measure 对比。
- 溢出报告模板里 label 与 metadata 的挂法（见坑 6/7）写进文档，防止后人踩。

**需要 spike 验证的假设**
- 标点悬挂/压缩（原生不支持，测字体 OpenType 效果与替代方案）。
- grid 固定列溢出视觉行为；place 画报定位在 0.15 基线改动下的偏移。
- 0.15 基线保留改动对固定帧内文本垂直度量的影响（回归比对 0.14）。
- universe 相关包（若有）在 0.15.1 的兼容性。

**版本锁定**：CI 用 `typst compile` + `typst eval` 双命令；锁定 typst 0.15.1（实测版本）并保留升级回归用例（0.11→0.15 的 breaking 已列，未来 0.16 需再查 changelog）。
