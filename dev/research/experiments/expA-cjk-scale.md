# 实验 A — autofit 字号缩放 × CJK 字体切换交互

> 日期：2026-08-07 · Typst 0.15.1 · 源文件：`expA-cjk-scale.typ`
> 登记风险 #2（framefit 缩放内嵌 ctyp 字体切换是否生效）

## 问题

framefit 用 `text(size: 1em * factor)` 包裹正文做 autofit 缩放。若正文含 CJK，内层 `show regex(...): set text(font: cjk)` 字体切换在缩放包裹下**是否仍生效**？若失效，中文会用默认字体渲染，破坏 N1 中英混排。

## 方法

`show regex("[\\p{Han}，。；：！？]+"): set text(font: "Noto Serif CJK SC")` 后，分别量 CJK 样本、拉丁样本、混合样本（缩放 1.1em）的行高。CJK 字体（Serif CJK）与默认字体行高不同，行高差异即证明字体切换是否生效。

## 结果

| 指标 | 值 |
|---|---|
| h-cjk（纯中文，Serif CJK） | 8.02pt |
| h-latin（纯英文，默认字体） | 7.51pt |
| h-mixed（缩放 1.1em 混合） | **8.82pt** |
| cjk-vs-latin-diff | 0.51pt |

**判定**：`h-mixed = 8.02 × 1.1 = 8.822 ≈ 8.82pt`——混合文本行高精确等于 **CJK 字体高 × 缩放系数**。说明 `show regex` 字体切换在 `text(size:)` 缩放包裹下**依然生效**（中文部分仍用 Serif CJK，只是整体放大 1.1×）。

## 结论

✅ **风险 #2 解除**：framefit 缩放 × ctyp 式字体切换可共存。中文在缩放时正确用 CJK 字体渲染。

## 对 presswire 的建议

- 任务 14（cjk.typ）可放心把 ctyp 的 `show regex` 字体切换放在 framefit 缩放包裹内。
- 缩放因子作用于 CJK 与拉丁同比例——中英混排的基线相对关系在缩放后保持。
