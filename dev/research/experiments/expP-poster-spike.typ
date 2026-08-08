// ============================================================
// 实验 P: 画报 mini-spike — place 贪心装配（任务 13 前置验证）
//
// 验证目标（对应 dev/p0.capacity.md + dev/research/experiments/expG-place.md）:
//   1. place 在 layout 回调内可用（固定版心 block 内绝对定位）
//   2. shelf worst-fit 贪心装配 ≥5 图片板块 + ≥3 文字板块，
//      无重叠 / 不越界 / 版心底部无空白带
//
// 结论文档: expP-poster-spike.md
// 运行: typst compile expP-poster-spike.typ（cwd = 本目录）
// 证据: 编译成功 + 断言通过 + metadata JSON + 渲染 PNG
// ============================================================
// 页面高度 660pt：保证标题(≈26pt) + 固定版心 560pt 放得下，
// 否则 breakable:false 的固定高块会跳到下一页（philosophy 坑 #4）
#set page(width: 440pt, height: 660pt, margin: 20pt)
#set text(font: "Noto Serif CJK SC", lang: "zh", region: "cn")

// ------------------------------------------------------------
// 1. 贪心装配核心：shelf worst-fit
//    坐标/尺寸全部用 float（pt 数值），发射时乘 1pt —— 规避
//    0.15 长度乘法受限（length × length 不可用）。
//    item  = (kind, w, h, c)    板块：类型/宽/高/内容
//    shelf = (y, h, used)       行：行顶 y / 行高 h / 已用宽 used
//    规则: 选「剩余宽度最大且放得下」的行（worst-fit）；
//          无行可放则另起新行，行高 = 行内最高板块。
//    校验: 两两矩形不交（无重叠）、全部落在 (0,0)-(W,H) 内（不越界）。
// ------------------------------------------------------------
#let shelf-worst-fit(items, W, H) = {
  let rows = ()
  let placed = ()
  let overflow = 0
  for item in items {
    let w = item.w
    let h = item.h
    let best = none  // (row-index, remaining-width)
    for i in range(rows.len()) {
      let r = rows.at(i)
      if W - r.used >= w and r.h >= h {
        if best == none or (W - r.used) > best.at(1) {
          best = (i, W - r.used)
        }
      }
    }
    if best != none {
      let i = best.at(0)
      let r = rows.at(i)
      placed.push((kind: item.kind, x: r.used, y: r.y, w: w, h: h, c: item.c))
      // 行容器不可变：整行重建（used += w）
      rows = range(rows.len()).map(k => {
        let rr = rows.at(k)
        if k == i { (y: rr.y, h: rr.h, used: rr.used + w) } else { rr }
      })
    } else {
      let y = if rows.len() == 0 {
        0.0
      } else {
        let last = rows.last()
        last.y + last.h
      }
      if y + h > H { overflow += 1 }
      rows.push((y: y, h: h, used: w))
      placed.push((kind: item.kind, x: 0.0, y: y, w: w, h: h, c: item.c))
    }
  }
  // ---- 校验: 重叠 / 越界 / 填充率 ----
  let overlap-free = true
  let in-bounds = true
  let used-bottom = 0.0
  for p in placed {
    if p.x < 0.0 or p.y < 0.0 or p.x + p.w > W or p.y + p.h > H { in-bounds = false }
    used-bottom = calc.max(used-bottom, p.y + p.h)
  }
  for i in range(placed.len()) {
    for j in range(i + 1, placed.len()) {
      let a = placed.at(i)
      let b = placed.at(j)
      if a.x < b.x + b.w and b.x < a.x + a.w and a.y < b.y + b.h and b.y < a.y + a.h {
        overlap-free = false
      }
    }
  }
  let area = 0.0
  for p in placed { area += p.w * p.h }
  (
    placed: placed,
    overlap-free: overlap-free,
    in-bounds: in-bounds,
    bottom-fill: used-bottom / H,   // 底部占用比（1 = 铺满到版心底）
    area-fill: area / (W * H),      // 面积填充率
    item-count: placed.len(),
    overflow-items: overflow,
  )
}

// ------------------------------------------------------------
// 2. 板块构造器（须在 layout 回调 / context 内调用，measure 需要 context）
// ------------------------------------------------------------

// 色块图片槽（代理真实图片：宽高已知，无需 measure）
#let img-slot(w, h, fill, txt) = (
  kind: "img",
  w: w,
  h: h,
  c: box(
    width: w * 1pt, height: h * 1pt,
    fill: fill, stroke: 0.5pt + rgb("#333333"), radius: 3pt,
  )[#align(center + horizon)[#text(size: 10pt, weight: "bold", fill: rgb("#ffffff"))[#txt]]],
)

// 真实图片（本地 SVG）：绝对宽度 + measure 得高（expM 定案：
// 百分比宽度在 measure 内解析为 0，绝对宽度可靠）
#let img-photo(w) = {
  let img = image("expP-img.svg", width: w * 1pt)
  let h = measure(img, width: w * 1pt).height.pt()
  (
    kind: "img", w: w, h: h,
    c: box(
      width: w * 1pt, height: h * 1pt,
      clip: true, stroke: 0.5pt + rgb("#333333"), radius: 3pt,
    )[#img],
  )
}

// 文字板块：measure 得自然高，宽度固定
#let txt-blk(w, size, weight, body) = {
  let content = text(size: size, weight: weight)[#body]
  let h = measure(content, width: w * 1pt).height.pt()
  (
    kind: "text", w: w, h: h,
    c: box(width: w * 1pt, height: h * 1pt)[#align(top + left)[#content]],
  )
}

// ------------------------------------------------------------
// 3. 主演示：固定版心 block + layout 回调 + place 装配
// ------------------------------------------------------------
#text(size: 13pt, weight: "bold")[expP 画报 mini-spike — place 贪心装配（shelf worst-fit，layout 回调内）]
#v(6pt)

#block(
  width: 400pt, height: 560pt,
  clip: true, breakable: false,          // 固定版心（p0 定案）
  stroke: 0.5pt + rgb("#888888"),
)[
  #layout(size => {
    let W = 400.0
    let H = 560.0
    let items = ()
    items.push(img-slot(400.0, 56.0, rgb("#3a5a78"), "题图横幅 400×56（full-bleed 带）"))
    items.push(img-slot(180.0, 110.0, rgb("#2b7a78"), "图 1 · 180×110"))
    items.push(txt-blk(180.0, 15pt, "bold", "画报版式试验：图片主导、标题凌驾、板块网格的贪心装配验证"))
    items.push(img-slot(100.0, 70.0, rgb("#8a5a44"), "图 2"))
    items.push(txt-blk(180.0, 9.5pt, "regular", "本段验证文字板块在贪心装配中的高度量测与行内拼接。文字高度由 measure 决定，行高自适应，不会与相邻板块重叠。"))
    items.push(img-slot(220.0, 120.0, rgb("#5a3a8a"), "图 3 · 220×120"))
    items.push(txt-blk(200.0, 9.5pt, "regular", "shelf worst-fit 的核心：每个板块放进「剩余宽度最大」的行，放不下就另起一行。行高取行内最高板块，保证任何时刻板块两两不交。"))
    items.push(img-photo(140.0))
    items.push(txt-blk(160.0, 9.5pt, "regular", "真实图片路径已打通：SVG 按绝对宽度加载，高度由 measure 取得，参与同一贪心装配。"))
    items.push(img-slot(120.0, 110.0, rgb("#8a5a1a"), "图 4 · 竖版"))
    items.push(img-slot(260.0, 80.0, rgb("#1a5a8a"), "图 5 · 260×80"))
    items.push(txt-blk(380.0, 8.5pt, "regular", "© 2026 presswire 排版引擎 · 本页为实验 P 渲染证据 · 全部板块坐标由算法计算，未手调。"))
    let plan = shelf-worst-fit(items, W, H)

    // 编译期断言: 任一失败 → 编译报错（「可行/降级」判定的机器证据）
    assert(plan.overlap-free, message: "expP: 板块重叠（place 贪心装配失败）")
    assert(plan.in-bounds, message: "expP: 板块越界（超出固定版心 400×560）")
    assert(plan.bottom-fill >= 0.85, message: "expP: 版心底部空白带过大（bottom-fill < 0.85）")

    let img-count = 0
    let text-count = 0
    for it in items {
      if it.kind == "img" { img-count += 1 } else { text-count += 1 }
    }

    [
      #for p in plan.placed [ #place(dx: p.x * 1pt, dy: p.y * 1pt, p.c) ]
      #metadata((
        "exp": "expP-poster-spike",
        "container": "layout-callback",
        "algo": "shelf-worst-fit",
        "plate-w": 400.0,
        "plate-h": 560.0,
        "item-count": plan.item-count,
        "img-blocks": img-count,
        "text-blocks": text-count,
        "overlap-free": plan.overlap-free,
        "in-bounds": plan.in-bounds,
        "bottom-fill": plan.bottom-fill,
        "area-fill": plan.area-fill,
        "overflow-items": plan.overflow-items,
        // 地面真值：每个板块的最终坐标（供下游坐标级校验 / 结论文档引用）
        "placed": plan.placed.map(p => (
          "kind": p.kind,
          "x": p.x, "y": p.y, "w": p.w, "h": p.h,
        )),
      )) <expP-meta>
    ]
  })
]
