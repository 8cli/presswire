# CJK universe 包兼容性调研（Typst 0.15.1）

> 日期：2026-08-07 · 实测环境：typst 0.15.1，Noto CJK 全套，编译在 /tmp/typst-cjk-spike/
> 目的：任务 14（cjk.typ）直接依赖包的 0.15.1 兼容性验证（**逐一编译冒烟**）

## 一、总览表

| 包 | 最新版 | 0.15.1 编译冒烟 | 结论 |
|---|---|---|---|
| `ctyp` | 0.3.1 | 0.3.1 **必崩**（title 键缺失）；0.3.0 / 0.2.0 ✅；0.3.1+补丁 ✅ | **用 0.3.0**，或 0.3.1+font-cjk-map 补丁 |
| `cjk-unbreak` | 0.2.3 | ✅（含传递依赖 touying 0.6.1） | 直接依赖，锁 0.2.3 |
| `cjk-unshrink` | 0.1.0 | ✅ | 直接依赖，唯一版本 0.1.0 |
| `cjk-spacer` | 0.2.1 | ✅（`\p{scx:Han}` 正则 + `cjk-latin-spacing` 参数均可用） | 直接依赖，锁 0.2.1 |

**四包组合同文档**（ctyp 0.2.0 + unbreak + unshrink + spacer）编译 ✅，show rule 无冲突。

## 二、每包详析

### ctyp ⚠️（最关键——有 bug + 虚构 API）
- **版本/许可/维护**：MIT；HPDell/ctyp（master 活跃 2026-07-02）；universe 6 版本，0.3.1（2026-03-17）`compiler = "0.14.1"`。
- **核心 API**（0.3.x，读 src/ctyp.typ 源码确认）——**计划里的 `ctyp-set(cjk-font:)` 是虚构 API**（0.1.0 起从未存在），实际：
  ```typ
  #import "@preview/ctyp:0.3.1": ctyp, page-grid
  #let (ctypset, cjk) = ctyp(       // 返回 (theme, font-utils) 二元组
    fontset-cjk: "noto",            // auto(默认Fandol) | "fandol/fangzheng/source/noto/windows/huawen" | dict
    font-latin: (:), font-cjk-map: (:),
    fix-list-enum: true, fix-smartquote: true, fix-first-line-indent: true,
    remove-cjk-break-space: true,   // 内置正则版断行空格移除（0.1.1 起）
    heading-numbering: none,        // 0.2.0 起, 支持中文编号
  )
  #show: ctypset
  #(cjk.hei)[黑体]                   // 字形工具: song/hei
  #show: page-grid.with(width: 42, height: 65, ..args)  // 版心网格→页边距
  ```
  fontset：`family` = 「字形(song/hei)→字体名+变体」映射；`map` = 「元素→字形:变体」映射。noto 集 = Noto Serif CJK SC(song) + Noto Sans CJK SC(hei)。
- **0.15.1 实测**：
  - `0.3.1` 裸用 `#show: ctypset` → **panic**：`dictionary does not contain key "title"` at `src/ctyp.typ:153`。根因：0.3.1 新增「title 元素字体支持」，`_font-latin-cover` 遍历 `("text","emph","strong","raw","heading","title")` 但 6 个打包 fontset 的 `map` 都缺 `title` 键 → **任何文档必崩**，与 Typst 版本无关。
  - **规避 A（推荐 0.3.0）**：`#import "@preview/ctyp:0.3.0": ctyp` → 编译 ✅（最新正常版本，含列表样式/标题编号，仅缺 title 字体）。
  - **规避 B（要 0.3.1 功能）**：`font-cjk-map: (title: (cjk: "hei", latin: "serif"))` → 编译 ✅（含 heading-numbering + page-grid + cjk.hei + 公式混排）。
  - master 已修复（noto.typ 含 title 键）但未发版，可等 0.3.2。
- **presswire 用法**：
  ```typ
  #import "@preview/ctyp:0.3.0": ctyp, page-grid
  #let (ctypset, cjk) = ctyp(fontset-cjk: "noto", remove-cjk-break-space: false)
  #show: ctypset
  #show: page-grid.with(width: 30, height: 45)  // 报纸版心
  ```

### cjk-unbreak
- **版本/许可**：0.2.3（最新，无 compiler 字段）；MIT；KZNS/cjk-unbreak（归属正确），main 最后提交 2026-03-17。
- **核心 API**：单函数 `remove-cjk-break-space(rest)`，**传递依赖 `@preview/touying:0.6.1`**（transform-childs.typ 里 import utils）。实现：transform-childs 递归遍历 content AST，删除 CJK 间断行空格。`str.ends-with(regex)` 用了 Typst 0.15.1 支持的语法。
- **0.15.1 实测**：✅ `#show: remove-cjk-break-space` 编译通过；touying 0.6.1 依赖一并通过。
- **用法**：`#import "@preview/cjk-unbreak:0.2.3": remove-cjk-break-space` + `#show: remove-cjk-break-space`。

### cjk-unshrink
- **版本/许可**：唯一 0.1.0；MIT；**实际作者 neruthes/typstpkg-cjk-unshrink**（计划写 KZNS 是错的，KZNS/cjk-unshrink 不存在）。
- **核心 API**：`cjk-unshrink(doc, alignment-table: (:), plain-汉字: true, plain-ひらがな: true, plain-カタカナ: true, plain-한글: false, aggregate-punctuation: false, debug: false)`，用法 `#show: cjk-unshrink.with(...)`。原理：每个 CJK 字符包 `box(width: 1em)` 防压缩；全角标点序列强制 1em 宽 box（默认居中，alignment-table 可改）。
- **0.15.1 实测**：✅ 编译通过（debug 与普通模式均验证）。
- **用法**：`#import "@preview/cjk-unshrink:0.1.0": cjk-unshrink` + `#show: cjk-unshrink.with()`（报纸正文建议 aggregate-punctuation: true + par(justify: true)）。

### cjk-spacer
- **版本/许可**：最新 0.2.1（`compiler = "0.14.0"`）；MIT；**实际作者 ryuryu-ymj/cjk-spacer**（计划写 KZNS 是错的）。
- **核心 API**：`#show: cjk-spacer`（参数 cjk-regex / western-open-punc-regex / western-close-punc-regex，均有默认）。原理：`set text(cjk-latin-spacing: auto)` + ghost 字符（measure([a]) 宽度 + `h(-w, weak: false)` 抵消）实现「公式与 CJK 间距」「半角括号与和文间距」「断行不加空格」。默认正则用 `\p{scx:Han}`——0.15.1 支持。
- **0.15.1 实测**：✅ 编译通过（含 `$E = m c^2$` 行内公式 + 半角括号 + 中英混排）。
- **用法**：`#import "@preview/cjk-spacer:0.2.1": cjk-spacer` + `#show: cjk-spacer`。

## 三、对 presswire 任务 14 的建议

**直接依赖 + 版本锁定（全 exact）**：

| 依赖 | 锁定版本 | 用途 | 备注 |
|---|---|---|---|
| ctyp | **0.3.0** | 中文字体切换 + page-grid | 0.3.1 裸用必崩；master 已修未发版 |
| cjk-unbreak | 0.2.3 | AST 级断行空格移除 | 传递依赖 touying 0.6.1（已验证） |
| cjk-unshrink | 0.1.0 | 全角标点防压缩 | 唯一版本 |
| cjk-spacer | 0.2.1 | 公式/CJK 间距 | 与 unbreak 功能 1 重叠 |

**cjk.typ 用法骨架**：
```typ
#import "@preview/ctyp:0.3.0": ctyp, page-grid
#import "@preview/cjk-unbreak:0.2.3": remove-cjk-break-space
#import "@preview/cjk-unshrink:0.1.0": cjk-unshrink
#import "@preview/cjk-spacer:0.2.1": cjk-spacer

#let (ctypset, cjk) = ctyp(fontset-cjk: "noto", remove-cjk-break-space: false)
#show: ctypset
#show: remove-cjk-break-space          // 替代 ctyp 内置正则版, AST 遍历更可靠
#show: cjk-unshrink.with()             // 全角标点防压缩
#show: cjk-spacer                      // 公式间距（unbreak 无此能力）
#show: page-grid.with(width: ..., height: ...)
```
四包组合已验证无冲突；`#(cjk.hei)[...]` 取字形工具函数（勿用 `cjk.hei[...]` 方法语法，Typst 字典键禁止方法调用）。

**已知坑清单**：
1. **ctyp 0.3.1 title bug**（最高优先）：裸用即 panic；规避 = 用 0.3.0 或传 `font-cjk-map: (title: ...)`；关注 0.3.2。
2. **计划文档 API 修正**：`ctyp-set(cjk-font:)` 不存在 → 用 `ctyp(fontset-cjk:)` 二元组 API；fontset 是 song/hei 双字形概念。
3. **仓库归属修正**：cjk-unshrink = neruthes/typstpkg-cjk-unshrink；cjk-spacer = ryuryu-ymj/cjk-spacer（均非 KZNS）。
4. **功能重叠**：cjk-unbreak 与 cjk-spacer 都处理断行空格（AST 遍历 vs 零宽空格 show rule）；spacer 独家是公式间距。建议两者同开（已验证共存）。
5. **字体**：ctyp `fontset-cjk: "noto"` 需 Noto Serif/Sans CJK SC（本机已装）；CI 需确认或换 `auto`（需 Fandol）。
6. 四包 compiler 字段均 ≤ 0.15.1，实测编译全通过即确认 0.15.1 兼容。
