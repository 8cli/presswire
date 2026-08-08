# 实验 P — 画报 mini-spike：place 贪心装配（任务 13 前置）

> 日期：2026-08-08 · Typst 0.15.1 · 分支 `wt/poster-mini-spike`
> 源文件：`expP-poster-spike.typ` + `expP-img.svg`
> 渲染证据：`expP-poster-spike-1.png`（100dpi）/ `expP-poster-spike-hi-1.png`（150dpi）
> 机器证据：`typst eval 'query(<expP-meta>).last().value' --in expP-poster-spike.typ --format json`

## 结论：✅ 可行

**固定版心（400×560pt，block clip + breakable:false）内，`place()` + shelf worst-fit 贪心装配可用，且完全满足任务 13 画报前置验收：**

| 验收项 | 标准 | 实测 |
|---|---|---|
| 图片板块数 | ≥5 | **7**（6 色块代理 + 1 真实 SVG `image()`） |
| 文字板块数 | ≥3 | **5** |
| 无重叠 | 两两不交 | ✅ 12 板块坐标级两两不交（`overlap-free: true`，编译期断言 + 像素复核） |
| 不越界 | 全部在版心内 | ✅ `in-bounds: true`（坐标级 + 像素级） |
| 无空白带 | 渲染无空带 | ✅ `bottom-fill: 0.902`（内容铺到版心 90.2% 高度，断言 ≥0.85）；`area-fill: 0.680` |
| place 在 layout 回调内可用 | 原 expG 遗留问题 | ✅ **可用**，坐标相对固定版心 block 内容区（原点=版心左上角） |

验证命令（cwd = `dev/research/experiments`）：

```bash
typst compile expP-poster-spike.typ          # 编译成功即断言全过（重叠/越界/空带任一失败会编译报错）
typst eval 'query(<expP-meta>).last().value' --in expP-poster-spike.typ --format json
pdftoppm -png -r 100 expP-poster-spike.pdf expP-poster-spike
```

地面真值（metadata `placed` 字段，版心相对坐标 pt）：

```
img  x=  0  y=  0  w=400 h= 56   （full-bleed 横幅）
img  x=  0  y= 56  w=180 h=110
text x=180  y= 56  w=180 h= 52.3 （大标题，与上图同行并排）
img  x=  0  y=166  w=100 h= 70
text x=100  y=166  w=180 h= 33.1
img  x=  0  y=236  w=220 h=120
img  x=220  y=236  w=140 h= 93.3 （真实 SVG，绝对宽 140pt，measure 得高）
text x=  0  y=356  w=200 h= 33.1
text x=200  y=356  w=160 h= 33.1
img  x=  0  y=389  w=120 h=110
img  x=120  y=389  w=260 h= 80
text x=  0  y=499  w=380 h=  6.2 （页脚行）
```

## 方法（任务 13 直接采用）

### 架构：layout 回调内"量测 → 贪心 → 发射 place"一步到位

```typst
#block(width: 400pt, height: 560pt, clip: true, breakable: false)[
  #layout(size => {
    let items = ()
    // 1) 构造板块：色块/图片/文字，宽高已知（文字/图片高度用 measure 量测）
    items.push(img-slot(400.0, 56.0, rgb("#3a5a78"), "题图横幅"))
    items.push(txt-blk(180.0, 15pt, "bold", "大标题……"))
    // 2) 贪心装配（见下）
    let plan = shelf-worst-fit(items, W, H)
    // 3) 编译期断言：任一失败 → 编译报错 = 「可行/降级」判定的机器证据
    assert(plan.overlap-free, message: "板块重叠")
    assert(plan.in-bounds,     message: "板块越界")
    assert(plan.bottom-fill >= 0.85, message: "底部空白带过大")
    // 4) 发射：坐标为 float（pt 数值），发射时 × 1pt
    [ #for p in plan.placed [ #place(dx: p.x * 1pt, dy: p.y * 1pt, p.c) ]
      #metadata((/* 证据 */)) <expP-meta> ]
  })
]
```

关键点：

1. **layout 回调自带 context**：`measure()` 可直接调用（无需再包 `#context`），回调返回值即发射内容。
2. **place 定位基准**：layout 元素在固定 block 的流内，`place` 的父容器解析到该 block → 坐标原点 = **版心内容区左上角**，`dx/dy` 即板块左上角绝对坐标（expG「相对父容器定位」在此成立）。
3. **place 不占流**：非浮动 place 覆盖式定位，layout 元素自身高度≈0，不影响固定版心几何。
4. **浮点几何**：坐标/尺寸全程用 float（pt 数值），发射时 `p.x * 1pt`。原因：0.15 的 `length × length` 报错（无 Area 类型），float 运算最省心；measure 高度用 `(…).height.pt()` 转 float。
5. **真实图片**（expM 定案延续）：`image(path, width: W_abs)` 绝对宽度 → `measure(img, width: W_abs).height` 得高，参与同一贪心；百分比宽度在 measure 内解析为 0，勿用。
6. **版本细节**：0.15.1 的 `box()` 无 `align` 参数——内容居中需 `[#align(center + horizon)[…]]`。

### 贪心算法：shelf worst-fit（核心函数）

```typst
#let shelf-worst-fit(items, W, H) = {
  let rows = ()        // shelf = (y, h, used)：行顶 / 行高 / 已用宽
  let placed = ()
  for item in items {
    let (w, h) = (item.w, item.h)
    let best = none    // (row-index, remaining-width)
    for i in range(rows.len()) {
      let r = rows.at(i)
      if W - r.used >= w and r.h >= h {
        if best == none or (W - r.used) > best.at(1) { best = (i, W - r.used) }
      }
    }
    if best != none {
      let i = best.at(0); let r = rows.at(i)
      placed.push((x: r.used, y: r.y, w: w, h: h, c: item.c))
      rows = range(rows.len()).map(k => {          // 行容器不可变：整行重建
        let rr = rows.at(k)
        if k == i { (y: rr.y, h: rr.h, used: rr.used + w) } else { rr }
      })
    } else {                                       // 无行可放 → 另起新行
      let y = if rows.len() == 0 { 0.0 } else { rows.last().y + rows.last().h }
      rows.push((y: y, h: h, used: w))
      placed.push((x: 0.0, y: y, w: w, h: h, c: item.c))
    }
  }
  // 校验 + 统计（overlap-free / in-bounds / bottom-fill / area-fill）见源文件
  …
}
```

- **worst-fit 语义**：候选行取「剩余宽度最大」者——把板块摊进最空的行，避免小板块堆死左侧、大板块无处安放。
- **无重叠保证**：行内 `x = used` 顺序排布 + 行高 = 行内最高板块 → 任何时刻两两不交（数学保证，另加坐标级断言兜底）。
- **不越界保证**：行内放不下（used + w > W）才开新行；新行 y = 已有行底。整页装不下时 `y + h > H` 计 overflow，断言兜底报错。
- **空白带控制**：行紧密堆叠（行间无间隙），底部剩余空间 = 版面自然留白，`bottom-fill` 量化。

### 固定版心纪律（p0 定案在本 spike 中的两个注意点）

1. `block(width, height, clip: true, breakable: false)` 成立：无推页、溢出被裁。
2. **⚠️ 坑 #4 复现**：固定高块若放不进页面剩余空间（如标题+6pt 后剩 554pt < 560pt），`breakable: false` 会让**整块跳到下一页**，首页留下大空白（spike 第一次编译即中招：PDF 2 页，首页只有标题）。→ presswire 必须保证**页面前置内容 + 版心高 ≤ 页面文本区高**，或版心块独占一页。

## 关键发现（2-3 条）

1. **place 在 layout 回调内可用，且坐标相对固定版心内容区**——expG 遗留问题关闭，任务 13 无需降级 grid 手排。贪心装配在 Typst 内**纯函数完成**（量测→算坐标→发射），无 state、无收敛风险。
2. **0.15 两个语法暗礁**：`box()` 无 `align` 参数（用 `align(…)` 内容包裹）；`length × length` 报错（几何运算统一用 float + `* 1pt` 发射 + `height.pt()` 取浮点）。
3. **文本高度 measure 与渲染一致（≤2pt 行盒舍入差）**：文字板块实际渲染行盒可能比 measure 结果低 1~2pt（末行底线）。5 个文字板块像素复核均在自身盒内或 ≤2pt 溢出，未造成相邻板块交叠；任务 13 生产实现建议给文字盒高度加 ~2pt 安全余量（或行高余量 0.2×line-height）。

## 遗留风险（非阻塞，任务 13 处理）

- **真实报纸图片的路径/缺失处理**：SVG 已打通（`image(path, width: 绝对)` + measure），但 PNG/JPEG 与缺失文件降级占位未测——沿用 expM 建议 + linotype 的占位策略。
- **贪心算法选型**：shelf worst-fit 在固定输入顺序下表现稳定（本 spike 12 板块全中）。真实内容高度不可控时，可加「按高度降序」等预排序变体；free-rect（guillotine 切分）变体在混合尺寸下碎片化严重，**不推荐**作为主算法。
- **含边距整页画报**：本 spike 验证的是版心内定位；若任务 13 需要定位到含边距整页，走 `page.foreground/background`（expG 建议），机制相同。
