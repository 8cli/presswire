#set page(width: 400pt, height: 400pt, margin: 15pt)

#context {
  let img = image("preview-p1.png")
  // 绝对宽度约束（非百分比）
  let w300 = measure(image("preview-p1.png", width: 300pt)).width
  let h300 = measure(image("preview-p1.png", width: 300pt)).height
  // 相对长度
  let w50pct_real = image("preview-p1.png", width: 50%).width
  metadata((
    "test": "expR5-image2",
    "w-300pt": w300,
    "h-300pt": h300,
    "w-50pct-content-width": w50pct_real,
  ))
}

#image("preview-p1.png", width: 300pt)
#v(4pt)
#text(size: 8pt, fill: gray)[300pt 绝对宽]
