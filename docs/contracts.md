# presswire 接口契约（任务 7b 冻结 — 并行开发前置门）

> 日期：2026-08-08 · 状态：**冻结**（支线任务 9/10/12/13/14/15 依赖此签名，改动需修订本文件 + 相关任务同步）
> 来源：任务 5（render_typst）/ 6（contracts）/ 7（plate.typ）实测定案

## 1. plate.typ — 固定版心函数

文件：`presswire_typst/plate.typ`

```typst
#let plate-frame(
  body,                    // [位置参数] 版内容 content（版头+栏体由任务 8 版式组装）
  plate-id,                // [位置参数] "plate-P1" 等（label 标识，eval query 取回）
  width: 390mm,            // 版心宽（单版 A3 横向 = paperW − 2·padSide）
  height: 261mm,           // 版心高（= paperH − padTop 20 − padBottom 16）
  severe-fill: 1.05,       // fill 超此值 panic（对应 latin truncated 5% 判定）
) = { ... }
```

- **报告通道**：`metadata((plate, fill, deficit_pt, overflow))` + 相邻 `label(plate-id)`，
  零尺寸 block 包住（须被布局才可 query）。
- **deficit_pt 为 length → JSON 字符串化**（`"341.18pt"`），Python 侧 `float(x.replace("pt",""))`。
- **严重溢出**（`overflow && fill > severe-fill`）→ `panic` → typst-py 捕获 `TypstError` → `sys.exit(1)`。
- 注意：Typst 参数语法——`body`/`plate-id` 是位置参数，**不能用 `body:` 命名传参**。

## 2. atoms.typ — 排版原子（任务 10 实现，签名预冻结）

文件：`presswire_typst/atoms.typ`（尚未创建，任务 10 按此签名实现）

```typst
#let kicker(text)                    // 眉题（小字号大写）
#let headline(text)                  // 主标题
#let subheadline(text)               // 副题
#let deck(text)                      // 导语段
#let byline(text)                    // 署名
#let storybyline(text)               // 副故事署名
#let dateline(text)                  // 日期线
#let expandedtitle(text)             // 展开标题
#let pullquote(text)                 // 引文块
#let photo(image-path, width-ratio, caption)  // 图片（width-ratio 0-1 × 版心宽 = 绝对宽，expM）
#let brief(label, items)             // 简讯块（label + items 数组）
#let inbrief(label, items)           // IN BRIEF 条（≤3 条一组）
```

- 原子只负责**渲染**（content），不负责版心/measure（plate-frame 管）。
- 富文本（markdown `**x**`/`*x*`）在原子内转 Typst markup：`**x**` → `*x*`（strong）、
  `*x*` → `_x_`（emphasis）；其余字符串已 `_escape`（code 字符串安全）。

## 3. 版式函数（任务 8 实现，签名预冻结）

文件：`presswire_typst/mainaside.typ` / `presswire_typst/columns.typ`（尚未创建）

```typst
#let render-mainaside(p)    // p: 版数据 dict（plates 数组元素）→ content
#let render-columns(p)      // p: 版数据 dict → content（等宽多栏，columns 字段控制）
```

- 返回 content，由 render-doc 包进 `plate-frame(body: <版式输出>, plate-id: "plate-P{n}")`。
- main-aside 侧栏收集用 `state()` 收集器（expL：`state("articles", ()).update(...)`）。

## 4. demand.json / layout.json — 契约结构（任务 6 定案）

文件：`presswire/contracts.py`

```json
// layout.json
{"sheets": {"front": ["p1","p2"], "back": ["p3","p4"]}, "layout": {"p1": "single", "p2": "multi"}}
//   - sheets: plates=2 且 ≥4 版 → front/back 分页；否则全 front
//   - layout: main-aside → "multi"，其他 → "single"

// demand.json
{"plates": {"P3": {"fill": 0.31, "deficit_pt": 84.2, "requests": [
  {"type": "brief", "count": 2, "words": [60, 90], "topic": "space", "min_kind": "agency"}]}}}
//   - 键 "P1".."P4"（P 前缀）；无需求（fill ≥ fill_min）→ 文件不存在（清空旧单）
//   - requests 规格: type(brief|main|deep_dive) × count × words[2] × topic × min_kind
//   - topic 映射: P1 world/military · P2 ai/tech · P3 space · P4 tech
//   - min_kind: P1 independent · P2 company · P3 agency · P4 tech-media
```

## 5. plates 数据形状（任务 5 定案）

`render_typst.py` 生成 `#let plates = ( ... )` 数组，每元素为 dict（字段顺序固定）：

```
kicker/headline/subheadline/deck/byline/date/body[]/pullquote/briefs[]/
mainbriefs[]/stories[]/layout/columns/expanded/image/imagewidth(默认"1.0")/
imagecaption
stories 元素: {headline, byline, body[]}（STORY-B/C 无 byline 键——latin 原样不对称，勿统一）
```

- 字符串值已 `_escape`（Typst code 字符串安全：`\\`→`\\\\`、`"`→`\"`，其余原样）。
- 富文本标记（`**x**`/`*x*`）在值里原样保留，由 atoms 原子转 markup。

## 变更规则

- 接口变更必须：改本文件 + 同步改 `.omo/plans/presswire.md` 对应任务 + 相关支线合并时处理。
- 并行支线（9/10/12/13/14/15）以本文件为唯一接口依据，不读主线实现。
