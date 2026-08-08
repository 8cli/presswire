// plate.typ — plate 环境: 固定版心 + 溢出 clip + metadata 报告（任务 7）
//
// 接口（任务 7b 冻结，并行支线依赖此签名）:
//   plate-frame(body, plate-id, width:, height:, severe-fill:)
//     body:       版内容 content（版头+栏体由任务 8 版式组装）
//     plate-id:   "plate-P1" 等（label 标识，eval query 取回）
//     width/height: 版心尺寸（默认单版 A3 横向 390×261mm，对应 latin
//                  contentW = paperW − 2·padSide = 420−30, contentH =
//                  paperH − padTop − padBottom = 297−20−16）
//     severe-fill: fill 超此值 panic（默认 1.05，对应 latin truncated 5% 判定）
//
// 报告通道（P0 定案）:
//   metadata((plate, fill, deficit_pt, overflow)) + 相邻 label(plate-id)
//   → typst eval 'query(metadata)' 全量取回（expB），Python 按 label 分组
//
// D4 红线（2026-08-07 实测修正）: #panic 使 CLI 退出码为 0——QA 门禁改用
//   typst-py 捕获: typst.compile() 遇 panic 抛 TypstError → Python sys.exit(1)。
//
// 注意: metadata 长度字段（deficit_pt）JSON 序列化为字符串（"12.5pt"），
//   Python 侧 float(x.replace("pt",""))。

#let plate-frame(
  body,
  plate-id,
  width: 390mm,
  height: 261mm,
  severe-fill: 1.05,
) = {
  context {
    // P0 测法 C: measure(内容, width: W).height 得自然高（固定版心不推页的前提）
    let natural-h = measure(body, width: width).height
    let fill = natural-h / height
    let deficit_pt = height - natural-h
    let overflow = natural-h > height

    // 报告通道（P0 定案: metadata 相邻 label，供 eval 'query(metadata)' 取回）
    // 零尺寸 block 包住（metadata/label 须被布局才可被 query 查到，且不占版面）
    block(width: 0pt, height: 0pt, breakable: false)[
      #metadata((plate: plate-id, fill: fill, deficit_pt: deficit_pt, overflow: overflow))
      #label(plate-id)
    ]

    // D4 红线: 严重溢出 → panic（typst-py 捕获 TypstError → sys.exit(1)）
    if overflow and fill > severe-fill {
      // length 转数字: x / 1pt → float（str 不接受 length 直接转换）
      panic(
        "严重溢出: " + plate-id + " 自然高 " + str(natural-h / 1pt)
        + "pt > 版心 " + str(height / 1pt) + "pt（fill " + str(fill) + "）"
      )
    }

    // 固定版心（H1 实证）: 含住溢出 + clip 截断 + 不跨页
    block(
      width: width,
      height: height,
      clip: true,
      breakable: false,
      fill: white,
      stroke: 0.5pt + rgb("#cccccc"),   // 调试边框（任务 9 theme 接管样式）
      inset: (x: 6pt, y: 4pt),
    )[#body]
  }
}
