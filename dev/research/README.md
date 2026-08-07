# presswire 开发难点调研

> 开始：2026-08-07 · 目的：系统性调研 presswire（Typst 报纸引擎）涉及的开发难点，避免掉坑
> 方法：**官方文档研究（代理并行）+ 本地实测（typst 0.15.1 实证）** 双通道交叉验证

## 目录结构

```
dev/research/
├── README.md                        # 本索引
├── philosophy/                      # 官方文档研究
│   ├── typst-official-docs-study.md # 官方文档直抓综合（measure/layout/context/query/block/show/place/grid/columns/text/math/page）
│   └── typst-philosophy-report.md   # 后台代理的完整避坑指南（完成时合并）
└── experiments/                     # 本地实测（typst 0.15.1 实证）
    ├── expA-cjk-scale.typ/.md       # autofit 缩放 × CJK 字体切换（风险#2 ✅解除）
    ├── expB-batch-query.typ/.md     # eval 批量 label 查询（风险#1 ✅解除）
    ├── expC-math-scale.typ/.md      # 公式随 text(size:) 缩放（U3 ⚠️ 经 expH 修正）
    ├── expC2-nested-fix.typ         # 早期实验（结论弃用, 见 expH）
    ├── expC3-text-nested.typ        # 早期实验（无约束 measure 异常假象）
    ├── expD-measure-width.typ/.md   # #7779 宽度溢出不影响高度量测（✅）
    ├── expE-framefit.typ/.md        # framefit 可用性 + API（✅ 任务11核心可用）
    ├── expF-breakable.typ/.md       # 固定高块 breakable 语义（✅）
    ├── expG-place.typ/.md           # place 定位（✅ 5场景+官方语义）
    ├── expI-typst-py-api.md         # typst-py query/eval API 验证（✅ 任务17关键）
    ├── expH-size-override.typ/.md   # measure 无约束嵌套异常 + U3 定案（✅ 关键发现）
    ├── expH2-showset-lock.typ       # show-set 锁公式字号（✅ 生效）
    ├── expH3-render.typ             # 渲染目检（内层 text 生效）
    ├── expH4-constrained.typ        # 有约束 measure 嵌套正常（✅）
    ├── expH5-math-lock-final.typ    # show-set 免疫外层缩放（✅）
    └── expH6-inner-lock-clean.typ   # 内层 text 锁公式无效（公式特例 ❌）
```

## 已解除的风险

| 原计划风险 | 结论 | 证据 |
|---|---|---|
| #2 framefit 缩放 × CJK 字体切换交互 | ✅ 生效 | expA：混合文本行高 = CJK 高 ×1.1 精确 |
| #1 typst eval 批量多 label 查询 | ✅ `query(metadata)` 全量 + Python 按 label 分组 | expB：4 版一次取回，label 字段在元素上 |
| #4 公式字号 × autofit 缩放 | ⚠️ **新发现**：公式随缩放（ratio 1.4），内层锁定无效 | expC/C2/C3，见下方 U3 对策 |
| typst-py 是否暴露 query API | ✅ **暴露 query + eval**（进程内，免子进程） | expI：README + 源码 query.rs 确认，与 CLI 同路径；`typst.eval(file, "query(metadata)")` 返回 JSON |

## 新发现的关键坑（expH 系列定案）

1. **measure 无约束时对嵌套 text 异常**（宽度/高度误判）——**必须带宽度约束**（presswire 恰好如此）。
2. **U3 定案**：`show math.equation: set text(size: 10pt)` 锁公式字号，**免疫外层缩放**（expH2/5）——任务 12 采用；内层 text 锁公式无效（expH6）。
3. **columns() 不均衡列高**（文档明说）——任务 8 需 spike 列分配行为。
4. **query 触发多遍编译**、自影响查询不收敛（5 次放弃）——任务 17 控制查询量。
5. **原生 covers 分字体**（`font: (name:, covers: "latin-in-cjk")`）+ `cjk-latin-spacing`——比 ctyp 正则更原生的 CJK 方案候选（任务 14）。

## 配套文档

- 计划风险登记：`.omo/plans/presswire.md`（本项目状态目录）
- 对比评估：`docs/comparison-linotype.md`
- P0 容量 spike：`dev/p0.capacity.md`

## 待合并

- [x] 本地实验（expA-F/H 系列）已入库
- [x] 官方文档直抓研究 → `philosophy/typst-official-docs-study.md`
- [x] 代理避坑指南 → `philosophy/typst-philosophy-report.md`（已合并）

## 两报告的交叉验证与差异

| 主题 | 两报告一致 | 差异/互补 |
|---|---|---|
| measure 溢出宽 #7779 | 约束宽裁剪、不可断长词单行高假阴性 | 代理有精确数值（30pt→30pt vs 自然 389.9pt）；本地 expD 同结论 |
| metadata 长度字符串化 | "992.22pt"/"410.1pt" 均为字符串 | 一致 |
| label 挂法 | markup 相邻，context 包装会挂到 context 元素 | 一致 |
| 公式字号 | 随 text(size:) 缩放 | 代理说 set math(size:) 无效；本地定案 show-set 锁字号（更强解法） |
| measure 无约束嵌套异常 | — | **本地独有发现**（expH：宽度 79.65pt 异常/高度误判，有约束正常） |
| 内层 text 锁字号 | — | **本地独有**（文本有效 expH4；公式无效 expH6） |
| 溢出检测 | 代理：锚点页差法对固定版心**不可用** | **重要**——修正计划任务 17（edwinhu 骨架 → measure 对比） |
| CJK | \p{Han} 可用、show-regex×text(size:) 兼容 | 本地补充 covers 原生分字体 + cjk-latin-spacing |
| 性能 | 1200 次 measure 仅 +4% | 24 步二分无压力 |
