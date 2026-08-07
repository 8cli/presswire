# 实验 M — 图片处理实测（任务 10 photo 原子 + 13 画报）

> 日期：2026-08-07 · Typst 0.15.1 · 源文件：`/tmp/typst-r2/image-test.typ` / `image-test2.typ`
> 测试图：`/home/yupeng/news/latex/assets/preview-p1.png`

## 问题

linotype 支持 `IMAGE`（路径）/`IMAGEWIDTH`（0-1 比例）/`IMAGECAPTION`，图片高度计入溢出检测（`\photo` 原子）。presswire 需验证 Typst 图片加载、measure 高度、宽度约束、路径解析。

## 实测结果

| 场景 | measure 结果 | 说明 |
|---|---|---|
| 自然尺寸 `image(path)` | 1190.81 × 842.54pt | ✅ 原图自然尺寸可测（宽高比 1.413） |
| **`image(path, width: 50%)`（百分比）** | **0 × 0pt** | ❌ **百分比宽度在 measure 上下文解析为 0** |
| `image(path, width: 300pt)`（绝对） | 300 × 212.26pt | ✅ 绝对宽度正常，保持宽高比 |
| `image(path, width: 50%).width`（content 属性） | `50% + 0pt` | 相对长度存为相对值，需布局上下文才解析 |

**核心发现**：`image()` 的**百分比宽度在 measure 内解析为 0**（measure 上下文无"容器宽度"可解析百分比）；**绝对宽度完全正常**。

## 对 presswire 的建议

1. **IMAGEWIDTH（0-1 比例）换算为绝对宽度**：render_typst 时根据版心宽 `contentW` 算出 `imagewidth × contentW`（如 `0.5 → image(path, width: 0.5*contentW)`）——**不用百分比**，measure 才可靠。
2. **图片高度参与溢出检测**：`measure(image(path, width: W_abs)).height` 可靠（实测 300pt 宽 → 212.26pt 高），直接用于任务 7 的 fill/deficit 计算。
3. **路径解析**：Typst 相对路径基于编译入口文件目录（`--root`/`--input` 控制）。presswire 的 `IMAGE` 相对路径需与 linotype 一致（plate 文件所在目录）——render_typst 时处理为相对编译入口的路径，或传 `--input` 映射。⚠️ **待 spike**：多目录 plates 时路径基准。
4. **图片裁剪**（超版心）：`image` 外层包 `block(width: W, height: H, clip: true)`——clip 隐藏超宽（与 expD 场景 A 一致：150pt 块内 300pt 宽盒被约束）。
5. **画报**（任务 13）：图片主导排版，`place` + `image(width: 绝对)` 组合——自然尺寸 measure 可用作贪心装配的输入（已知每图宽高比）。

## 与 linotype 的对应

- linotype `\photo{path}{width}{caption}` → presswire `image(path, width: W_abs)` + caption 原子。
- linotype 图片高度计入溢出 → presswire `measure(image(...)).height` 计入 fill。
- 血泪风险：linotype 有图片路径/缺失处理；presswire 需同款（image 文件缺失时报错或降级占位）。
