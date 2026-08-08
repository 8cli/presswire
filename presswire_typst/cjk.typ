// ============================================================
// cjk.typ — presswire 任务 14：CJK 中英混排集成模块
//
// 版本锁定（全 exact，见 dev/research/philosophy/cjk-universe-compat.md）：
//   ctyp        0.3.0   0.3.1 有 title 键 bug 裸用必崩，勿升
//   cjk-unbreak 0.2.3   AST 级断行空格移除（替代 ctyp 内置正则版）
//   cjk-unshrink 0.1.0  全角标点防压缩 / 聚合
//   cjk-spacer  0.2.1   CJK×公式 / 半角括号间距
//
// 用法（在文档中 import 本模块，模块顶层 show 规则自动全局生效）：
//   #import "../../presswire_typst/cjk.typ": *
//   #set page("a4")                       // 页面几何（或由 presswire 模板设置）
//   #show: cjk-page-grid.with(width: 42, height: 66)   // 可选：版心网格→页边距
//   #(cjk-font.hei)[黑体标题]  #(cjk-font.song)[正文宋体]
//
// 注意：模块内不得写死页面尺寸（报纸版心由调用方决定），
//       故 page-grid 以再导出形式暴露，而非直接 show。
// ============================================================
#import "@preview/ctyp:0.3.0": ctyp, page-grid
#import "@preview/cjk-unbreak:0.2.3": remove-cjk-break-space
#import "@preview/cjk-unshrink:0.1.0": cjk-unshrink
#import "@preview/cjk-spacer:0.2.1": cjk-spacer

// --- ctyp 二元组：(theme show 规则, 字形工具 dict) ---
// fontset-cjk: "noto" = Noto Serif CJK SC(song) + Noto Sans CJK SC(hei)
// remove-cjk-break-space: false → 弃 ctyp 内置正则版，改用 cjk-unbreak 的 AST 版
#let (ctypset, cjk-font) = ctyp(
  fontset-cjk: "noto",
  remove-cjk-break-space: false,
  fix-first-line-indent: true,
  fix-list-enum: true,
  fix-smartquote: true,
  heading-numbering: none,
)

// --- 四条 show 规则（模块顶层 show 规则在 import 后对整篇文档生效）---
#show: ctypset                      // ctyp 主题：字体映射 + 标点修正 + 段首缩进
#show: remove-cjk-break-space       // cjk-unbreak：AST 遍历删除 CJK 间断行空格
#show: cjk-unshrink.with(aggregate-punctuation: true)   // 全角标点防压缩 + 序列聚合
#show: cjk-spacer                   // cjk-spacer：CJK×公式/半角字符间距（unbreak 无此能力）

// --- 再导出给调用方 ---
#let cjk-page-grid = page-grid      // #show: cjk-page-grid.with(width:, height:)
