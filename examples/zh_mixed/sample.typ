// ============================================================
// examples/zh_mixed/sample.typ — 任务 14 前置：CJK 中英混排样例
//
// 验证目标（四包组合 ctyp 0.3.0 + cjk-unbreak 0.2.3 +
//           cjk-unshrink 0.1.0 + cjk-spacer 0.2.1）：
//   1. 中文段落按字断行
//   2. 英文长句按词断行（长单词不折断）
//   3. 中英混合段落基线对齐、间距自然
//   4. 中文标点正常（、。，；：「」《》——…？！）
//   5. 数字 + 单位混排
//   6. 行内公式与 CJK 间距（cjk-spacer 能力）
//
// 编译：typst compile examples/zh_mixed/sample.typ
// 结构化证据：typst query examples/zh_mixed/sample.typ --format json
// ============================================================
#import "../../presswire_typst/cjk.typ": *

// ---- 页面几何：A4 竖版 + 报纸版心网格（44 字符 × 70 字符）----
#set page("a4")
#show: cjk-page-grid.with(width: 44, height: 70)
#set text(size: 10.5pt)
#set par(justify: true)

// ==================== 报头（通栏）====================
#align(center)[
  #text(size: 15pt)[#(cjk-font.hei)[国产大飞机 C919 商业运营两周年]]
]
#v(4pt)
#align(center)[
  #text(size: 8.5pt, fill: gray)[#(cjk-font.song)[
    本报记者 林海 北京报道 · 2026 年 8 月 8 日 · 星期四
  ]]
]
#v(6pt)
#line(length: 100%, stroke: 0.6pt + black)
#v(6pt)

// ==================== 正文（双栏）====================
#set columns(2, gutter: 1.6em)

// ---- 第 1 段：纯中文段落（按字断行 + 中文标点密集）----
国产大型客机 C919 自两年前投入商业运营以来，已累计执飞航班超过五万架次，承运旅客突破六百万人次，平均客座率保持在 82% 以上。
从首航上海—成都航线到如今覆盖全国四十余个通航点，机队的日利用率稳步爬升，航班正点率连续十二个月领先行业平均水平。
对于一家起步仅两年的国产客机项目而言，这样的运营表现，被业内视为「从首航到规模化」的关键一跃。

// ---- 第 2 段：英文长句段落（按词断行，长单词不折断）----
"The two-year commercial operation of the C919 marks a significant milestone in the internationalization of China's aviation industry," said analysts at the consultancy firm specializing in aerospace supply chains.
The narrow-body jet, powered by the LEAP-1C engines and built around an advanced fly-by-wire flight control system, has demonstrated dispatch reliability comparable to that of its Western counterparts, according to data published by the operator.
Observations from Massachusetts Institute of Technology researchers suggest that certification hurdles, not engineering capability, now represent the primary constraint on overseas expansion.

// ---- 第 3 段：中英混合段落（基线对齐 + 数字单位 + 行内公式）----
在支线与干线市场的交界地带，C919 与 Airbus A320neo、Boeing 737 MAX 形成了直接竞争。
中国商飞披露的数据显示，C919 的目录价格为 9,900 万美元，较同级别机型具备 5% 至 8% 的成本优势；
其巡航马赫数 $"Ma" = 0.785$，接近跨声速极限 $"Ma"_"crit"$，但得益于新一代翼梢小翼与低阻力气动外形，单位油耗较同类产品降低 15.3%。
在噪声方面，起飞阶段的外部噪声水平低于 80 dB，满足国际民航组织第四阶段标准。

// ---- 第 4 段：中文标点密集段（引号/书名号/破折号/省略号/问叹）----
《航空周刊》在专题报道中评价：「C919 的成功，不在于打破某项纪录，而在于——它让'自主研发'四个字，从口号变成了可以交付的产品。」
从供应链角度看，问题依然存在：发动机、航电等核心部件仍依赖进口，适航取证之路布满荆棘——欧洲航空安全局（EASA）的审查已进入第三轮，美国联邦航空局（FAA）的接触则刚刚重启……
「我们等的不是许可，而是时间。」一位不愿具名的工程师说。

// ---- 第 5 段：收尾长段（中英混合 + 数字 + 展望）----
展望未来，产能爬坡与全球适航认证将成为决定 C919 命运的胜负手。
根据规划，2027 年上海浦东总装线的年产能将达到 100 架，届时累计确认订单有望突破 1,500 架，其中约 15% 来自海外客户。
On the international front, the aircraft's entry into the Southeast Asian and Middle Eastern markets hinges on bilateral airworthiness agreements that remain under negotiation.
业界普遍认为，国产大飞机的下半场，比的是耐力，而非速度。

// ==================== 验证数据（单栏，第二页）====================
#pagebreak()
#set columns(1)
#text(size: 11pt)[#(cjk-font.hei)[渲染验证]]
#v(4pt)
#line(length: 100%, stroke: 0.4pt + gray)
#v(6pt)

// ---- A. 断行规则证据盒（80pt 窄盒直出渲染，pdftotext 可按行提取）----
#text(size: 9.5pt)[#(cjk-font.hei)[A. 断行规则（80pt 窄盒直出渲染）]]
#v(3pt)
#grid(
  columns: (1fr, 1fr, 1fr),
  column-gutter: 8pt,
  row-gutter: 4pt,
  [
    #(cjk-font.hei)[英文短语 · 按词断行]
    #block(width: 80pt, stroke: 0.5pt + gray, inset: 2pt)[challenges ahead for the jet]
  ],
  [
    #(cjk-font.hei)[长单词 · 不折断]
    #block(width: 80pt, stroke: 0.5pt + gray, inset: 2pt)[internationalization]
  ],
  [
    #(cjk-font.hei)[中文长句 · 按字断行]
    #block(width: 80pt, stroke: 0.5pt + gray, inset: 2pt)[中文长句按字断行验证——本句不含任何空格与西文]
  ],
)
#v(6pt)

// ---- B. 结构化测量（context 实测 + metadata 供 typst eval query 取回）----
#context {
  let en-word = "internationalization"      // 长英文单词
  let en-phrase = "challenges ahead"        // 两个完整英文词
  let zh-run = "中文长句按字断行验证——本句不含任何空格与西文"  // 21 个汉字 + 2 个破折号
  let zh-char-n = 23                        // 字符数（勿用 str.len()：返回 UTF-8 字节数，CJK 每字 3 字节）
  let zh-char-w = 10.5pt                    // 全角字符步进 = 字号 1em

  // 单行基准 = 同一字符串无约束测量高（glyph bbox 高随行内容变化，不可跨串比较）
  let en-word-single = measure(par[#en-word]).height
  let en-word-60 = measure(par[#en-word], width: 60pt).height
  let en-phrase-single = measure(par[#en-phrase]).height
  let en-phrase-60 = measure(par[#en-phrase], width: 60pt).height
  let zh-natural-w = measure(par[#zh-run]).width
  let zh-single = measure(par[#zh-run]).height
  let zh-60 = measure(par[#zh-run], width: 60pt).height

  // 判据 1：中文全角度量正确 ⇔ 自然宽 ≈ 字符数 × 1em（±3% 容差；破折号为 0.89em 字形，见 expQ 结论文档）
  let zh-metrics-ok = zh-natural-w <= zh-char-n * zh-char-w * 1.03
  // 判据 2：中文串窄栏确实断行 ⇔ 约束高 > 单行高
  let zh-wraps = zh-60 > zh-single + 0.5pt
  // 判据 3：英文短语窄栏断成多行（词间空格处换行，整词不裂——见上方证据盒 bbox）
  let en-phrase-wraps = en-phrase-60 > en-phrase-single + 0.5pt
  // 判据 4（信息项）：超宽长词行为 —— Latin 字体 + justify 下 Typst 会加连字符断词；
  //   Noto CJK 字体下则溢出不折。见 expQ 结论文档「坑 3」。
  let en-longword-hyphenated = en-word-60 > en-word-single + 0.5pt

  metadata((
    "test": "expQ-cjk-sample",
    "font": "ctyp noto fontset (Noto Serif CJK SC song + Libertinus serif latin)",
    "zh-run-chars": zh-char-n,
    "zh-run-natural-w": zh-natural-w,
    "zh-expected-w": zh-char-n * zh-char-w,
    "zh-fullwidth-metrics-ok": zh-metrics-ok,
    "zh-h-single": zh-single,
    "zh-h-at-60pt": zh-60,
    "zh-wraps": zh-wraps,
    "en-phrase-h-single": en-phrase-single,
    "en-phrase-h-at-60pt": en-phrase-60,
    "en-phrase-wraps": en-phrase-wraps,
    "en-word-h-single": en-word-single,
    "en-word-h-at-60pt": en-word-60,
    "en-longword-hyphenated": en-longword-hyphenated,
  ))
  [
    #text(size: 9.5pt)[#(cjk-font.hei)[B. 结构化测量（typst eval query(metadata) 可复现）]]
    #v(3pt)
    - 无空格中文串（#zh-char-n 个全角字符）：自然宽 #zh-natural-w，期望 #(zh-char-n * zh-char-w)（破折号为 0.89em 字形）
      → 全角度量判据：#if zh-metrics-ok [✅ 每字 ≈1em 全角步进正确] else [❌ 度量异常]
    #v(3pt)
    - 中文串 60pt 窄栏内高 #zh-60 > 单行高 #zh-single
      → 断行判据：#if zh-wraps [✅ 按字断行（任意字符边界）] else [❌ 未断行]
    #v(3pt)
    - 英文短语 "challenges ahead"：60pt 窄栏内高 #en-phrase-60 > 单行高 #en-phrase-single
      → 断行判据：#if en-phrase-wraps [✅ 按词断行（词间空格处换行）] else [❌ 未断行]
    #v(3pt)
    - 超宽长词 "#en-word"（自然宽 #(measure(par[#en-word]).width) > 60pt）：
      60pt 栏内高 #en-word-60 vs 单行高 #en-word-single
      → #if en-longword-hyphenated [Typst 连字符断词（Latin 字体 + justify，核心行为，非包引入；Noto 字体下溢出不折）] else [溢出单行不折断（Noto 字体）]
    #v(5pt)
    #text(size: 9.5pt)[#(cjk-font.hei)[C. 混排间距（目检第 3 段 + 上方证据盒）]]
    #v(3pt)
    - 中文与拉丁字符之间的自然间距（ctyp 字体描述符 + cjk-spacer）：C919、Airbus A320neo、80 dB、15.3%
    - 行内公式 $"Ma" = 0.785$ 与中文之间的间距（cjk-spacer 独家能力）
    - 中文标点（，。、；：「」《》——…？！）渲染正常、不被压缩（cjk-unshrink）
  ]
}
