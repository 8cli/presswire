// ============================================================
// 实验 R5: 图片处理（任务 10 photo 原子 + 13 画报）
// 验证: image() 加载、measure 高度、宽度约束
// ============================================================
#set page(width: 400pt, height: 400pt, margin: 15pt)

#context {
  let img = image("preview-p1.png")
  let w = measure(img).width
  let h = measure(img).height
  let w50 = measure(image("preview-p1.png", width: 50%)).width
  let h50 = measure(image("preview-p1.png", width: 50%)).height
  metadata((
    "test": "expR5-image",
    "natural-w": w,
    "natural-h": h,
    "w-50pct": w50,
    "h-50pct": h50,
    "aspect-ratio": w / h,
  ))
}

// 渲染: 原图 + 50% 宽
#image("preview-p1.png")
#v(6pt)
#image("preview-p1.png", width: 50%)
#v(6pt)
#text(size: 8pt, fill: gray)[R5: image 加载 + 宽度约束]
