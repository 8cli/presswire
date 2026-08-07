# presswire vs linotype — 全面评估

> 日期：2026-08-07 · 依据：linotype 实际源码（build.py 771 行 + linotype.cls 907 行）与 presswire 计划
> 目的：记录 presswire 与 linotype 的相同点与核心差异，作为项目设计决策的权威参考。

## 一句话总评

> **presswire 是「同一契约、不同引擎哲学」的重新实现**——CLI 面与数据契约二进制兼容（imposer 零改动），但排版内核从「LaTeX 流水排版 + 外部编译循环 + 日志正则反馈」换成「Typst 原生块模型 + 单次编译内 measure 二分 + 结构化 metadata 反馈」。**共性在契约层，差异全在内核层。**

## 一、相同点（契约层，D2 红线保证）

| 契约面 | 一致性 |
|---|---|
| CLI 参数 | `--docopts/--visual/--demand/--no-autofit/--theme` 全套一致（presswire cli.py 桩已对齐） |
| plates 格式 | `parse_plate` 逐行移植，5 fixture + 8 真实日版 **0 差异**（不新增字段） |
| demand.json | `{plates:{P3:{fill,deficit_pt,requests}}}` 结构一致（任务 6 契约） |
| layout.json | sheets/layout 结构一致（任务 6） |
| 视觉 QA | pixelcheck 协议保持（--visual 消费 layout.json） |
| 纪律目标 | 固定版心不推页 + 溢出可测可报 + 纸张硬约束 |

## 二、核心差异（内核层）

| 维度 | linotype (LaTeX) | presswire (Typst) |
|---|---|---|
| **编译模型** | **3–16 次 xelatex 完整编译**（每次迭代=生成→编译→日志正则反馈，状态靠文件传递） | **单次 typst compile**，framefit 在 `layout` 回调内 24 步 measure 二分（内存内状态） |
| **溢出检测** | 日志 regex 解析 `typeout` 字符串（血泪 #41：微超 33.7pt 曾误杀 P2 补稿单） | `#metadata`+`#label` → `typst eval` JSON（结构化、P0 已证完整 value 提取） |
| **固定版心** | `\@colht`/`\@colroom` hack + `vsplit` 截断 + multicol boxed 绕行（血泪 #1/#5/#26/#28，约 30 条 TeX 语义坑） | `block(width,height,clip:true,breakable:false)` **原生原语**（P0 三假设全成立） |
| **autofit 旋钮** | 字号二分（每档一次完整编译，0.1pt 精度）+ 栏数 2–4 + bottommargin [12,16]mm | framefit 字号二分（单编译内）+ **one-liner 线性初值**（收敛 24 步→~6 步） |
| **溢出策略** | Overfull 警告 + vsplit 截断（可接受微超 <5%，5% 是"设计内正常"） | 收敛不到 → clip + metadata 报告 + 严重溢出 panic（退出码非0，QA 门禁） |
| **CJK** | 无原生处理（xelatex + 手动字体切换） | ctyp 正则切换 + cjk-unbreak/unshrink/spacer 全套（**新能力 N1**） |
| **数学公式** | 无管件 | Typst 原生 `$...$` + `math.size` 约束（**新能力 N2**） |
| **画报排版** | 无 | poster.typ place/grid（**新能力 N3**，高风险自研） |
| **字体** | 可变字体 xdvipdfmx 坑（需实例化脚本） | 可变字体原生支持 |
| **转义** | `tex_escape` 就地（`\`、`{}`、`$`） | `_escape()` 占位，任务 5 换 Typst 转义（反引号/`$`/`<`/`>`） |
| **依赖规模** | TeX Live（GB 级）+ multicol | typst CLI 单二进制 + universe 包（framefit/ctyp/cjk-*） |

## 三、最关键的 3 个差异

### 1. 反馈回路：文件传递 vs 内存内 measure —— 债务消除的本质

```
linotype 一次 autofit 迭代:
  generate_tex → write_tex → xelatex 编译(秒级) → 读 .log → 正则解析 → 决定下一档
  → 3-16 次循环，状态在文件系统之间往返

presswire 一次 autofit 迭代:
  framefit 的 layout 回调内: measure(width, text(size: factor)) → 二分下一档
  → 24 步全在 Typst 进程内，单次编译收敛
```

linotype 的每次迭代都是**完整编译**，这就是 U6「3–16 次 xelatex 对比单次」的债务根源；presswire 把「编译—反馈」闭环压进了一次编译的 measure 层。

### 2. 溢出可见性：字符串日志 vs 结构化 JSON

linotype 的反馈依赖 `\typeout` 消息的**字符串格式**，解析脆弱（血泪 #41 曾把 33.7pt 微超误判为严重溢出、误杀 P2 补稿单；血泪 #55 vsplit 截断静默丢内容但 fill 假达标）。presswire 的 metadata+label 通道是**结构化数据**（`{"fill":0.9,"deficit":"12.5pt","overflow":true}`），P0 已实证 `typst eval 'query(<label>)'` 返回完整 value，无字符串解析层。且 edwinhu 模式的**锚点页差检测**（相邻标签页差>1=溢出）比"测内容高"更稳——这能力 linotype 完全缺失（它只能靠 vsplit 截断后反推）。

### 3. 版心纪律的实现成本：30 条血泪 vs 1 个原语

linotype 的固定版心是**对抗 LaTeX 流水排版默认行为**的结果：`\@colht` 栏高预算、`vsplit` 截断、`multicol boxed` 绕行、`\global\setbox` 防回滚、`\if@linotype@multicol` 跳过 vsplit……55 条血泪中约 30 条是纯 TeX 语义坑。presswire 用 `block(width,height,clip:true,breakable:false)` **一个原语**达成同等纪律（P0 exp1 单页 vs exp1b 自动高度 5 页对照实证），clip 与报告还天然解耦。

## 四、风险与收益对照

### presswire 相对 linotype 的**新风险**（尚未踩坑）

| 风险 | 严重度 | 缓解 |
|---|---|---|
| `typst eval` 多 label 批量查询 JSON 结构 | 🟠 | 任务 17 前 spike |
| framefit 字号缩放 × CJK 字体切换交互 | 🟠 | 任务 14 前 15 分钟实测 |
| 画报 2D 矩形拼版自研（Typst 生态无现成） | 🟠 | 任务 13 前 mini-spike |
| 公式字号与 autofit 旋钮联动（U3） | 🟠 | `set math(size: 1em)` 约束 |
| typst-py query API 未验证 | 🟡 | 退回子进程调 eval |

### linotype 的**已付成本**（presswire 免除）

- 55 条血泪的踩坑史（约 30 条 TeX 语义 + 15 条管线契约）
- 每次 autofit 3–16 次 GB 级 TeX Live 编译
- 可变字体实例化、TEXINPUTS 路径锁定、pdfLaTeX 拒绝等运维债务

## 五、结论

1. **相同的是「什么」**：契约、纪律目标、QA 门禁、imposer 协议——presswire 站在 linotype 的契约肩膀上。
2. **不同的是「怎么」**：引擎从 LaTeX 流水排版换成 Typst 块模型，把「外部编译循环 + 字符串日志反馈」换成「单次编译内 measure + 结构化 metadata」，把「30 条血泪堆出来的固定版心」换成「1 个原生原语」。
3. **本质**：presswire 不是翻译 linotype，而是**用 Typst 的原生语义重新表达 linotype 用 TeX hack 达成的排版纪律**——这正是 D1「行为等价非像素级 Xerox」的落点。
4. **代价**：linotype 的 TeX 坑是已知的（踩过了），presswire 的 Typst 坑是未知的（P0 已排除最大风险，但 framefit×CJK、画报、eval 批量仍是开放项）——**风险从「已知的 55 条血泪」换成了「5 个登记在册的未知项」**。
