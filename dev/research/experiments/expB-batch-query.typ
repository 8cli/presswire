// ============================================================
// 实验 B: typst eval 批量多 label 查询（登记风险 #1）
// 验证: 多 label 一次性查询的 JSON 结构
// ============================================================
#set page(width: 300pt, height: 300pt, margin: 15pt)

// 多个 plate 的 metadata + label（模拟 4 版报纸）
#metadata((plate: "P1", fill: 0.95, deficit: 0pt, overflow: false))
#label("plate-P1")
#v(20pt)

#metadata((plate: "P2", fill: 0.72, deficit: 30.5pt, overflow: true))
#label("plate-P2")
#v(20pt)

#metadata((plate: "P3", fill: 1.0, deficit: -5pt, overflow: false))
#label("plate-P3")
#v(20pt)

#metadata((plate: "P4", fill: 0.5, deficit: 100pt, overflow: true))
#label("plate-P4")
