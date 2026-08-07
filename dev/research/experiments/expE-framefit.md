# 实验 E — framefit 实际可用性验证

> 日期：2026-08-07 · Typst 0.15.1 · 源文件：`expE-framefit.typ`

## 问题

任务 11 计划用 framefit 做 autofit 核心（单次编译内二分收敛）。但 universe 缓存为空——需要确认：① 包能否拉到；② 正确 API 签名；③ 在 presswire 固定版心模式下是否可用。

## 结果

1. **包可拉取** ✅：`@preview/framefit:0.1.0` 自动下载（6.2 KiB），缓存于 `~/.cache/typst/packages/preview/framefit/`。
2. **正确 API 签名**（读 lib.typ 源码确认）：
   ```
   fit-copy(min: 70%, max: none, max-lines: none, steps: 24,
            only-if-overflow: false, body)
   ```
   - **无 `width`/`height` 参数**——在 `layout(size => ...)` 回调内用内容可用尺寸作目标 frame。
   - `min`/`max` 是**比例**（ratio），不是绝对长度；`max: none` 时先倍增找上界（32 步）再二分。
   - `only-if-overflow: true`：先测 100% 是否装得下，装得下不缩放。
3. **核心算法确认**（lib.typ `_fits`）：
   ```typst
   measure(width: size.width, text(size: 1em * factor)[#body])
   ```
   ——**正是 P0 测法 C 的模式**（`measure(content, width: W)`），验证了 P0 选型与 framefit 内部一致。
4. **固定版心内编译成功** ✅：`block(width: 250pt, height: 330pt, clip, breakable: false)` 包裹 `fit-copy(min: 50%, max: 100%, only-if-overflow: true)` → 1 页 PDF，无报错，单次编译收敛。

## 结论

✅ **任务 11 的核心依赖可用**：framefit 拉取成功、API 明确、算法与 P0 测法 C 一致、固定版心模式单次编译收敛。**framefit 与 presswire 的固定版心原语（block + clip + breakable:false）直接兼容。**

## 对 presswire 的建议

- 任务 11 直接用 `fit-copy`，**min/max 用比例**（如 `min: 50%, max: 100%`），`only-if-overflow: true` 默认开（内容不满不缩放）。
- **溢出报告仍要自己加**：framefit 只缩字号不报溢出（收敛不到时 `panic`）。presswire 需在 fit-copy 外层的 block 用 P0 的 `measure` + metadata 报告 fill/deficit（实验 B 已定批量查询通道）。
- one-liner 线性初值（任务 11 调研补充）可作 `fit-copy` 前的一次 measure 预判——但 framefit 的二分已含 `only-if-overflow` 快速路径，初值优化优先级可降低。
- **max 上限建议**：`max: 100%`（不放大字号），配合 `min: 50%`——溢出收缩、太空不放大，符合报纸"填充优先"纪律。
