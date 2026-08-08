# 实验 Q：CJK 四包组合中英混排样例验证（任务 14 前置）

> 日期：2026-08-08 · 环境：typst 0.15.1（/usr/local/bin/typst），Noto Serif/Sans CJK SC 系统字体已装
> 目的：验证 cjk-universe-compat.md 定案的四包组合（ctyp 0.3.0 + cjk-unbreak 0.2.3 + cjk-unshrink 0.1.0 + cjk-spacer 0.2.1）在 presswire 场景下**实际可用**，并用一篇中英混排长文验证渲染正确性
> 产物：`presswire_typst/cjk.typ`（集成模块）+ `examples/zh_mixed/sample.typ`（样例，编译产出 sample.pdf 已被 .gitignore 忽略）

## 一、结论

**✅ 四包组合可用**（ctyp 0.3.0 + cjk-unbreak 0.2.3 + cjk-unshrink 0.1.0 + cjk-spacer 0.2.1，全 exact 锁定，编译零错误）。

- 模块化 import 成立：cjk.typ 顶层四条 show 规则在 `#import` 后**对整篇文档全局生效**（Typst 模块顶层 show 规则语义），调用方无需重复书写。
- ctyp `(ctypset, cjk-font)` 二元组 API 验证通过：`#show: ctypset` + `#(cjk-font.hei)[...]` / `#(cjk-font.song)[...]` 字形工具均正常。
- page-grid 再导出设计成立：模块内不写死版心，调用方 `#show: cjk-page-grid.with(width: 44, height: 70)`（单位 = 字符数）自行决定。
- 中文正文/英文长句/混合段/中文标点/数字单位/行内公式全部正确渲染（见第三节验证证据）。

## 二、样例结构

```
presswire_typst/cjk.typ          # 集成模块：import 四包 + 顶层 show 规则 + 再导出
examples/zh_mixed/sample.typ     # 样例：A4 竖版 + 版心网格 44×70 字符，双栏报纸式排版
examples/zh_mixed/sample.pdf     # 编译产出（gitignore 忽略）
```

正文 5 段覆盖验证矩阵：① 纯中文段（按字断行 + 标点密集）② 英文长句段（按词断行）③ 中英混合段（基线 + 数字单位 + 行内公式 `$"Ma" = 0.785$`）④ 中文标点密集段（「」《》——…？！）⑤ 收尾混合段。第二页为渲染验证页（窄盒直出证据 + context 结构化测量）。

编译命令（相对 import 逃不出项目根，必须 `--root`）：
```bash
typst compile --root . examples/zh_mixed/sample.typ
typst eval --format json --in examples/zh_mixed/sample.typ --root . 'query(metadata).map(m => m.value)'
```

## 三、渲染验证结果

### 3.1 结构化测量（typst eval query(metadata) 取回，全部通过）

| 判据 | 期望 | 实测 | 结果 |
|---|---|---|---|
| 中文全角度量 | 23 字符 ≈ 23 × 10.5pt = 241.5pt | 236.08pt（±2%，破折号为 0.89em 字形，见坑 5） | ✅ |
| 中文窄栏断行 | 60pt 栏内高 > 单行高 | 66.73pt > 7.89pt | ✅ 按字断行 |
| 英文短语断行 | "challenges ahead" 60pt 栏内 2 行 | 20.64pt > 6.91pt | ✅ 按词断行 |
| 超宽长词 | 自然宽 84.9pt > 60pt 栏宽 | 20.64pt ≠ 6.91pt | ℹ️ 连字符断词（见坑 3） |

### 3.2 文本提取（pdftotext）证据

- **中文按字断行**：第一段在任意字符边界断行（「…承运旅客突破六百万／人次，…」「…这一行为决定…」），无词间空格的中文串正常。
- **英文按词断行**：第二段整词换行（"…the internationalization of／China's aviation industry,"…），长单词 intact。
- **中文标点**：「」《》——…？！，。、；全部正常出现；`’`/`“”` 为 typographic 引号（pdftotext 扁平化显示，渲染为正确字形）。
- **数字 + 单位**：82%、9,900 万美元、5% 至 8%、0.785 马赫、15.3%、80 dB、100 架、1,500 架、15% 均正常。
- **行内公式**：`Ma = 0.785`、`Ma_crit` 正常渲染（提取扁平化为 "Macrit" 属 pdftotext 行为）。

### 3.3 基线对齐（pdftotext -bbox 几何证据）

混合行「在支线与干线市场的交界地带，C919／Airbus A320neo、Boeing 737 MAX／形成了直接竞争。」：

- CJK 字形段 yMin=294.82 yMax=305.32；Latin 字形段 yMin=294.67 yMax=306.64 —— 同一行、同一基线（yMax 差 = 两种字体的 descent 差异，Latin 下行字母如 g/y 超出 CJK em 盒是正常排版）。
- 纯中文行与混合行行高一致（11.97pt），行距均匀 —— ctyp 字体描述符 + Noto 字体度量兼容。

### 3.4 窄盒断行证据（样例第二页 A 区）

- 80pt 盒「challenges ahead for the jet」→ `challenges ahead / for the jet`（整词换行，bbox 证实 "challenges" 与 "ahead" 为完整单词）✅
- 80pt 盒「internationalization」→ `internationaliza-tion`（Typst 连字符断词，核心行为）ℹ️
- 80pt 盒「中文长句按字断行验证——本句不含任何空格与西文」→ 7 字/行 × 4 行，任意字符边界 ✅

## 四、踩坑记录

1. **`#if` 块内 `set`/`show` 规则不生效（实验方法坑，非包坑）**：Typst 的 `set`/`show` 在代码块内是**块级作用域**，`#if cond { set par(justify: true) }` 对块后内容无效（静默 no-op）。初期用 `--input` 开关切换四包的探针全部因此测了个寂寞——**四包组合行为完全一致**的假象由此而来。修正：直接顶层 `#set`/`#show`。这是 Typst 语义，写主题函数/条件编译时必须注意。

2. **`measure(text(...))` 不参与断行**：`text()` 元素在宽度约束下**溢出而不换行**；要测断行必须用 `measure(par[...], width:)`。且 `measure(par[...])` 单行返回 **glyph bbox 高**（10.5pt 字约 7.6-7.9pt，非行盒 14.7pt），跨字符串不可比 —— 判据一律用「同一字符串约束/无约束比较」或「>单行高」，不可用「总高 ÷ 行高」数行数。

3. **超宽英文词行为分叉（Typst 0.15 核心行为，非包引入）**：
   - ctyp `latin: "serif"` 解析为默认字体 **Libertinus Serif**（font-latin 空字典时 "serif" 按字体名传给 Typst → 未命中 → 回退默认），`par(justify: true)` 下超栏宽长词**自动加连字符断词**（"internationalization" → "internation-alization"，PDF 内含 soft hyphen U+00AD）。对报纸是**有利**行为。
   - 显式 Noto Serif CJK SC 字体下则**溢出单行不折词**（Noto 无断词支持）。任务 14 正文若想强制不折词，需注意该分叉；新闻栏宽下正常英文词几乎不会触发。

4. **`str.len()` 返回 UTF-8 字节数**：`"中文长句…".len()` = 69（23 字 × 3 字节）而非 23。数字符数需自行按 cluster 统计（`str.clusters().len()`），或直接硬编码/按 1em 换算。样例 metadata 因此硬编码 `zh-char-n = 23` 并注释说明。

5. **中文破折号 "—" 在 Noto Serif CJK SC 中为 0.89em 字形**（非全角 1em）：23 字串自然宽 236.08pt vs 期望 241.5pt，差 5.42pt = 2 个破折号各窄 2.71pt。字体度量，非包问题；判据用 ±3% 容差。

6. **相对 import 逃不出项目根**：`examples/zh_mixed/sample.typ` 里 `#import "../../presswire_typst/cjk.typ"` 必须 `--root .` 编译（默认 root = 主文件目录）。presswire 构建脚本需注意传 `--root`。

7. **`typst query` 需要 selector 参数**；查 metadata 用 `typst eval --format json --in file.typ --root . 'query(metadata).map(m => m.value)'`（0.15.1 实测可用，JSON 值中 length 序列化为 "84.9pt" 字符串）。

8. **cjk-font 字形工具只收 `(body, weight, latin)`**：`#(cjk-font.hei, size: 15pt)[...]` 直接报错；要套字号/颜色须外层包 `#text(size: 15pt)[#(cjk-font.hei)[...]]`。参考文档「勿用 `cjk.hei[...]` 方法语法」同源——字典键是函数，非方法。

9. **模块顶层 show 规则 import 后全局生效**（正验证而非坑）：cjk.typ 四条 show 规则无需调用方重写；page-grid 因需调用方定版心而作再导出（`#let cjk-page-grid = page-grid`）。

10. **cjk-unshrink 逐字 box 化的提取噪音**：窄盒中文每字包 `box(width: 1em)`，pdftotext 提取出现字间空格（如「行 验 证」），属提取产物；渲染（PDF 字形 + bbox 几何）无多余空隙。

## 五、对任务 14 的落地建议

1. **cjk.typ 按当前骨架直接进任务 14**：四包锁版、二元组 API、page-grid 再导出、`aggregate-punctuation: true` 均实测通过；唯一待定项是版心网格参数由 presswire 模板传入。
2. **字体**：ctyp `fontset-cjk: "noto"` 本机直接可用；CI 需保证 Noto Serif/Sans CJK SC 安装（scripts/ci-install-fonts.sh 已含）。
3. **正文建议** `par(justify: true)`（配合 unshrink 聚合标点 + 中文两端对齐），英文超宽词自动连字符断词可接受；如需禁用，改用 Noto 字体作 Latin 覆盖。
4. **构建脚本**：相对 import 场景必须 `--root <repo>`，否则编译报 "would escape the project root"。
5. **后续监控**：ctyp 0.3.2 发版后可重新评估 0.3.1 title 键 bug 是否修复（0.3.0 保持可用，不阻塞）。

## 附：复现命令

```bash
cd <repo>
typst compile --root . examples/zh_mixed/sample.typ     # 产出 2 页 PDF
pdftotext -layout examples/zh_mixed/sample.pdf -        # 断行/标点提取
pdftotext -bbox examples/zh_mixed/sample.pdf -          # 基线几何证据
typst eval --format json --in examples/zh_mixed/sample.typ --root . \
  'query(metadata).map(m => m.value)'                    # 结构化判据
```
