# presswire 开发难点调研

> 开始：2026-08-07 · 目的：系统性调研 presswire（Typst 报纸引擎）涉及的开发难点，避免掉坑
> 方法：**官方文档研究（代理并行）+ 本地实测（typst 0.15.1 实证）** 双通道交叉验证

## 目录结构

```
dev/research/
├── README.md                        # 本索引
├── philosophy/                      # 官方文档研究（后台代理产出）
│   └── typst-philosophy-report.md   # Typst 哲学与开发算法研究（避坑指南）
└── experiments/                     # 本地实测（typst 0.15.1 实证）
    ├── expA-cjk-scale.typ/.md       # autofit 缩放 × CJK 字体切换（风险#2 ✅解除）
    ├── expB-batch-query.typ/.md     # eval 批量 label 查询（风险#1 ✅基本解除）
    ├── expC-math-scale.typ          # 公式随 text(size:) 缩放（U3 风险 ⚠️）
    ├── expC2-nested-fix.typ         # 内层 text 锁定公式字号（无效 ❌）
    └── expC3-text-nested.typ/.md    # 内层 text(size:) 覆盖普遍性（外层赢）
```

## 已解除的风险

| 原计划风险 | 结论 | 证据 |
|---|---|---|
| #2 framefit 缩放 × CJK 字体切换交互 | ✅ 生效 | expA：混合文本行高 = CJK 高 ×1.1 精确 |
| #1 typst eval 批量多 label 查询 | ✅ `query(metadata)` 全量 + Python 按 label 分组 | expB：4 版一次取回，label 字段在元素上 |
| #4 公式字号 × autofit 缩放 | ⚠️ **新发现**：公式随缩放（ratio 1.4），内层锁定无效 | expC/C2/C3，见下方 U3 对策 |

## 新发现的关键坑（U3 需重新设计）

**公式字号无法通过内层 `text(size:)` 锁定**——最外层 `text(size:)` 直接参数覆盖所有内层（expC3 纯文本确认是普遍行为）。U3「公式不随正文字号旋钮缩放」需重新设计，4 个对策见 `experiments/expC-math-scaling.md`。

## 配套文档

- 计划风险登记：`.omo/plans/presswire.md`（本项目状态目录）
- 对比评估：`docs/comparison-linotype.md`
- P0 容量 spike：`dev/p0.capacity.md`

## 待合并

- [x] 本地实验（expA/B/C/C2/C3）已入库
- [ ] 后台代理的官方文档调研报告 → `philosophy/`（完成时合并）
