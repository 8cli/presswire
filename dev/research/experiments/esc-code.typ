#set page(width: 400pt, height: 500pt, margin: 15pt)

// code 模式字符串字面量转义测试（render_typst 真实用法）
#let s1 = "美元 \$ 井号 \# 反斜杠 \\ 反引号 \` 方括号 \[x\]"
#let s2 = "尖括号 \<x\> 星号 \*x\* 下划线 \_x\_"
#let s3 = "花括号 \{x\} 百分号 \% 与号 \&"

#text(size: 10pt)[s1: #s1]
#v(4pt)
#text(size: 10pt)[s2: #s2]
#v(4pt)
#text(size: 10pt)[s3: #s3]
#v(8pt)

// markup 模式: 反斜杠转义特殊字符
#text(size: 10pt)[
  markup: 美元 \$ 井号 \# 方括号 \[x\] 反引号 \`x\` 星号 \*x\* 下划线 \_x\_ 尖括号 \<x\> 花括号 \{x\}
]
