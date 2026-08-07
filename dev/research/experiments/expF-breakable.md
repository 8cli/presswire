# 实验 F — breakable 对固定高度 block 的语义（版心纪律完整画像）

> 日期：2026-08-07 · Typst 0.15.1 · 源文件：`expF-breakable.typ`

## 问题

P0 验证了 presswire 目标配置 `block(width, height, clip: true, breakable: false)` 单页含住溢出。但 `breakable: true` 是否会让固定高度块跨页？clip 与 breakable 的相互作用是什么？这决定 presswire 是否必须强制 `breakable: false`。

## 结果

| 场景 | 配置 | 所在页 |
|---|---|---|
| A | 固定高 + clip + **breakable: false** | 页 1 |
| B | 固定高 + clip + **breakable: true** | **页 1**（不跨页） |
| C | 固定高 + 无 clip + breakable: true | 页 2（块整体流式换页） |

- 总页数 2（3 块 × 100pt + 标签 > 单页内容区 257pt，正常流式分页）。
- **关键**：B（breakable: true）仍在页 1——**固定高度块 + clip 即使允许 breakable 也不跨页**，溢出被 clip 裁掉。
- C 在页 2 是**块整体**移到下一页（流式布局的 normal 行为），不是块内内容跨页。

## 结论

✅ **固定高度 block 无论 breakable/clip 何种组合，块内内容都不跨页**（高度是硬约束）。clip 只决定溢出内容**可见/隐藏**。这与 P0 exp1/1c 结论一致，补全了 breakable 语义画像：

```
固定高度 block 语义 = 高度硬约束（永不块内跨页）
  ├── clip: true  → 溢出裁剪（presswire 默认）
  ├── clip: false → 溢出可见（溢出内容会画出块外，可能重叠后续内容）
  └── breakable   → 不影响固定高度块的块内跨页行为（仅影响无高度约束时的分页）
```

## 对 presswire 的建议

- presswire 的 `plate.typ`（任务 7）**固定用 `clip: true, breakable: false`**——虽然后者非必需，但显式声明意图、防未来有人改配置。
- **clip 与报告解耦**（P0 决策）再次确认：clip 只管视觉裁剪，溢出报告走 metadata（实验 B 通道）。
- 若未来需要「溢出内容在下一页续排」（linotype 的 vsplit 续排语义），**固定高度块做不到**——需要无高度约束 + 手动分栏。这是 presswire 与 linotype 的一个行为差异点：linotype 靠 vsplit 截断丢弃（不续排），presswire 靠 clip 裁剪（同样不续排），**两者都是丢弃语义**，契约一致。
