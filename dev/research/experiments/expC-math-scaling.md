# 实验 C / C2 / C3 — 数学公式字号 × autofit 缩放（U3 关键）

> 日期：2026-08-07 · Typst 0.15.1 · 源文件：`expC-math-scale.typ` / `expC2-nested-fix.typ` / `expC3-text-nested.typ`
> 登记风险 #4 + **U3 验收标准的关键风险**：公式字号不随正文字号旋钮缩放

## 问题

U3 要求「公式字号不随正文字号旋钮缩放」。framefit 用 `text(size: 1em * factor)` 包裹正文缩放。问题是：
1. 公式高度是否随 `text(size:)` 缩放？（expC）
2. 能否用**内层** `text(size: 10pt)` 锁定公式字号，使外层缩放不影响它？（expC2/expC3）

## 实验 C — 公式随 text(size:) 缩放

| 场景 | 公式高 |
|---|---|
| h-math at 10pt | 6.83pt |
| h-math at 14pt | 9.56pt |
| ratio（块级） | **1.4**（= 14/10，完全线性缩放） |
| ratio（内联） | **1.4** |

**结论 C**：公式**随 `text(size:)` 线性缩放**（ratio 恰 = 字号比）。U3「公式不随旋钮缩放」**不会自动成立**。

## 实验 C2 — 内层 text(size:) 锁定（公式场景）

| 场景 | 公式高 |
|---|---|
| base 10pt | 6.83pt |
| 外层 9pt 缩放 | 6.15pt |
| 外层 9pt + 内层 `text(size: 10pt)` 锁定 | **6.15pt**（锁定无效） |
| inner-lock-recovery | **-0.68pt**（未恢复） |

**结论 C2**：内层 `text(size: 10pt)` **无法**覆盖外层 `text(size: 9pt)` 缩放——公式仍按外层 9pt 渲染。

## 实验 C3 — 纯文本隔离（确认普遍性）

| 场景 | 行高 |
|---|---|
| t10（纯 10pt） | 6.58pt |
| t9（纯 9pt） | 5.92pt |
| t9in10（外层 9pt + 内层 10pt） | **5.92pt**（= t9，内层无效） |
| t10in9（外层 10pt + 内层 9pt） | **6.58pt**（= t10，内层无效） |

**结论 C3**：这是 **Typst 普遍行为**——**最外层 `text(size:)` 直接参数覆盖所有内层 `text(size:)`**（无论嵌套 text 还是公式）。内层锁定字号不可行。

## 综合结论（⚠️ 2026-08-07 经 expH 系列修订）

**本文件部分结论已由 expH 系列（expH-size-override.md）修正**：

- ✅ 保留：公式随 `text(size:)` 缩放（expH6 干净验证：9pt=6.15 / 10pt=6.83）。
- ❌ 修正：「内层 `text(size:)` 锁定无效」**对公式成立**（expH6：6.15pt 未恢复），但 **expC2 的结论源于无约束 measure 异常，需弃用**（expH1/H3/H4 显示无约束 measure 嵌套 text 异常、渲染正常、有约束正常）。
- ✅ 定案：**U3 的解法是 show-set 锁定**——`show math.equation: set text(size: 10pt)` 对外层缩放免疫（expH2/expH5 实证 6.83pt 锁定）。

### 修正后的对策（任务 12 采用）

1. **show-set 锁定公式字号**（推荐，官方方式，实测有效）：
   ```typst
   #show math.equation: set text(size: 10pt)
   ```
2. 内层 `text(size:)` 锁公式**无效**（公式元素不吃 text 直接参数），勿用。
3. 文本内容字号锁定可用内层 `text(size:)`（有约束 measure 实证有效）。
4. 所有 measure 带宽度约束（避开无约束嵌套异常）。

## 附：实验中发现的 Typst 语义细节

- `#set math(size: 10pt)` **非法**（`math` 是模块不是元素，`error: expected function, found module`）。
- `math(...)` 也不是函数，不能 `measure(math(...))`——直接 `measure($...$)` 或 `measure(text(size:, $...$))`。
- 含 `set` 规则的代码块 `{ set text(...); expr }` 返回 **content 而非 expr 值**（`let h = { set ...; measure(...) }` 是 content，不能参与计算）——用 `text(size:, ...)` 包裹代替。
- metadata 键名含连字符必须带引号（`"math-in-text-1.4em-h"`），否则被解析为减法。
