// ============================================================
// 实验 R4: state() 收集器模式（任务 8 mainaside 侧栏收集）
// 验证: 从正文任意位置收集文章到侧栏（dashing-dept-news 模式）
// ============================================================
#set page(width: 400pt, height: 400pt, margin: 15pt)

// 收集器: state 存内容数组
#let collect(entry) = state("articles", ()).update(prev => prev + (entry,))

// 文章原子: 渲染时同时收集到 state
#let article(title, body) = {
  collect((title: title, body: body))
  block(width: 100%, stroke: 0.5pt + gray, pad(6pt)[
    #text(size: 11pt, weight: "bold")[#title]
    #v(4pt)
    #body
  ])
}

// 正文流式写入（收集器模式: 文章在任意位置定义）
#article("头条一", lorem(15))
#v(8pt)
#article("头条二", lorem(20))
#v(8pt)

// 侧栏: 渲染时读取收集的内容（放文末模拟侧栏）
#block(width: 100%, fill: rgb("#eee"), pad(8pt)[
  #text(size: 10pt, weight: "bold")[侧栏收集结果]
  #v(4pt)
  #context {
    let arts = state("articles", ()).get()
    arts.map(a => [#text(size: 9pt)[• #a.title] #v(2pt)])
  }
])

// metadata 报告 state 内容数（验证收集是否成功）
#context metadata(("test": "state-collector", "collected": state("articles", ()).get().len()))
