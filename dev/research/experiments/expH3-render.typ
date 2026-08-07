// ============================================================
// 实验 H3: 嵌套 text 渲染目检（H1 异常值复核）
// ============================================================
#set page(width: 400pt, height: 200pt, margin: 15pt)

#text(size: 9pt)[PURE9: Hello]
#v(4pt)
#text(size: 10pt)[PURE10: Hello]
#v(4pt)
#text(size: 9pt)[NESTED: #text(size: 10pt)[Hello]]
#v(4pt)
#text(size: 9pt)[EM-NESTED: #text(size: 1.111em)[Hello]]
