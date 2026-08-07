# 实验 O — 标题宽度 + 双版并排（任务 15/16 前置）

> 日期：2026-08-07 · Typst 0.15.1 · 源文件：`expO1-headline-width.typ` / `expO2-side-by-side.typ`

## O1 — 中文标题在固定栏宽的换行/超宽（任务 15）

### 实测数据

| 标题 | 自然宽（单行） | 150pt 约束高 | 折行 |
|---|---|---|---|
| 中文「三中全会部署进一步全面深化改革」（14 字） | 165pt | 23.19pt | 2 行 |
| 英文「China's Economy Shows Resilience Amid Global Uncertainties」 | 332.98pt | 38.36pt | 3 行 |
| 中英混合「国产大飞机C919完成商业首航 Beijing-Shanghai」 | — | — | 2 行（正确断行） |

**渲染确认**（pdftotext）：
```
中文标题:
三中全会部署进一步全面深
化改革                    ← 中文正确折 2 行
英文标题:
China's Economy Shows
Resilience Amid Global
Uncertainties              ← 英文正确折 3 行
中英混合:
国产大飞机 C919 完成商业首
航 Beijing-Shanghai        ← 中英混合正确断行
```

### 结论
✅ **中英文标题在固定栏宽都正确换行**（中文按字折行、英文按词折行、混合正确断行）。任务 15 机制成立：
- **超宽检测**：`measure(text(title)).width`（无约束）vs 栏宽——超宽即需 one-liner 缩放或折行（expO1 数据：中文 165pt > 150pt → 折 2 行）。
- **折行控制**：中文自然折行（按字），可接受；如需单行（one-liner 场景）再缩放。
- 注意：中英混合标题 CJK 与 Latin 间有自动间距（`cjk-latin-spacing`），折行正确。

## O2 — plates=2 双版并排（任务 16 契约）

### 方案（验证成功）
```typst
#grid(
  columns: (1fr, 10pt, 1fr),   // 左版 | 栏缝 | 右版
  [
    #block(width: 100%, height: 250pt, clip: true, breakable: false,
           stroke: ..., inset: 8pt)[#lorem(60) #label("plate-P1")]
  ],
  [],                          // 栏缝
  [#block(...#lorem(80) #label("plate-P2"))],
)
```

### 实测数据
- P1 自然高 151.12pt / P2 自然高 194.28pt，帧高 250pt → **均不溢出**。
- **每版独立 overflow 报告**（metadata 含 P1/P2 各自 fill/deficit，P0 通道）。
- 单页 1 张（双版并排达成 linotype 的 plates=2 语义）。

### 结论
✅ **grid 双版并排 + 独立固定版心 + 独立溢出报告** 完全可行。任务 16 的 plates=2 契约机制成立：
- 两两配对（P1|P2, P3|P4）由 render_typst 循环生成 grid 行。
- 每版独立 `#label("plate-PN")` → eval 批量取回各自 fill（expB 通道）。
- 栏缝用 grid 中间空列（10pt）——与 linotype `\colGap` 对应。

## 对 presswire 的完整建议

- **任务 15**：`measure(text(title)).width` 超栏宽 → one-liner 缩放（min 下限）或接受折行；中文按字折行天然。
- **任务 16**：plates=2 用 `grid(1fr, gap, 1fr)` 生成，每版独立块 + label；溢出各自报告。
- 两实验都印证：**固定版心 + 溢出报告 + 双版并排 = presswire 版面纪律的三大块全部有实证**。
