# presswire 计划修订与决策记录

> 日期：2026-08-07 · 目的：沉淀调研（GitHub 生态 + Typst 哲学/实测）对 presswire 计划的全部修订与依据
> 说明：编排层完整计划（22 任务 + F1-F3、依赖矩阵、验收）位于本项目编排目录 `.omo/plans/presswire.md`（不在本仓库）；**本文档镜像其中因调研而修订的关键决策**，供仓库读者与后续执行者查阅，避免重复调研。

## 一、修订总览

| 时间 | 触发 | 修订范围 |
|---|---|---|
| 2026-08-07 早 | P0 spike 完成 | P0 段结论回写；任务 7/17 API 决策（eval 通道） |
| 2026-08-07 早 | 计划审查 | 依赖矩阵 16 补 6；U5/U7 编号；测试数量按实点；任务 2/3 环境约束 |
| 2026-08-07 午 | GitHub 生态调研 | 复用清单全面更新（one-liner 初值 / edwinhu / dashing-dept-news / 画报自研） |
| 2026-08-07 午 | Typst 哲学/实测调研 | 任务 12 show-set 锁公式；任务 17 measure 对比；风险登记 5 解除 4 新增 |

## 二、P0 结论回写（前置门，✅ 已完成）

P0 spike（`dev/p0.capacity.md`）三个假设全成立，阻塞解除：

1. **H1 固定版心不推页**：`block(width, height, clip: true, breakable: false)` 单页含住溢出（exp1 1 页 vs exp1b 自动高度 5 页对照）。
2. **H2 溢出可测可报**：`measure(content, width: W).height`（测法 C）返回自然高度（exp1: 1092.22pt / CJK exp3: 545.1pt）；`#metadata` + 相邻 `#label` → `typst eval 'query(<label>)'` 取完整 value。
3. **H3 宽度风险不阻断**：exp4 证实宽度溢出场景 measure 全安全，#7779 不阻断高度量测。

**API 决策**：① 溢出量测 `measure(content, width: W).height`，复杂布局退回深度块测；② 报告通道 `#metadata((fill, deficit)) #label("<id>")` + `typst eval 'query(<label>)'`（`typst query` 弃用禁用）；③ clip 与报告解耦；④ CJK 无特例。

## 三、任务级修订

### 任务 7 — plate.typ（固定版心 + 溢出报告）
- 采用 P0 测法 C：`measure(内容, width: W)`。
- 报告通道：`#metadata` 相邻 `#label("<plate-id>")`，`typst eval 'query(<plate-id>)'` 取 value。
- **注意**：metadata 长度字段 JSON 序列化为字符串（`"12.5pt"`）→ Python `float(x.replace("pt",""))`。
- 严重溢出 panic（退出码非 0）。

### 任务 11 — autofit（framefit）
- 直接依赖 `@preview/framefit:0.1.0`（实测可用，expE：拉取成功、固定版心内单次编译收敛）。
- **加 one-liner 线性初值**（调研新结论）：1 次 measure 得初值 → framefit 邻域二分（24 步 → ~6 步）。
- framefit 签名（读源码确认）：`fit-copy(min: ratio, max: ratio|none, max-lines, steps: 24, only-if-overflow: false, body)`——**min/max 是比例非长度**；`only-if-overflow: true` 先测 100%。
- 建议 `max: 100%`（不放大）、`min: 50%`（溢出收缩）。
- framefit 只缩字号**不报溢出**——溢出报告靠任务 7 的 measure + metadata。

### 任务 12 — math.typ（U3 定案，2026-08-07 实测）
- **`#show math.equation: set text(size: 10pt)` 锁公式字号，免疫 autofit 外层缩放**（expH2/5 实证：外层 `text(size: 9pt)` 包裹下公式仍 6.83pt = 10pt 高）。
- 内层 `text(size:)` 锁公式**无效**（expH6：公式元素不吃 text 直接参数）。
- `set math(size:)` **非法**（math 是模块非元素，实测报错）。
- 公式随 `text(size:)` 缩放（ratio 1.4 线性）——因此**必须 show-set 锁定**才能满足 U3「不随旋钮缩放」。

### 任务 13 — poster.typ（画报，高风险自研）
- **Typst 生态无现成 2D 矩形拼版**（仅 AGPL rjldtp 可借贪心 worst-fit 思路 + biceps flex-wrap）。
- 任务 13 前先做 **mini-spike**（1 个样例版验证 `place()` 贪心可行）。
- place 机制要点：相对父容器定位；顶层 = 页面文本区；**整页含边距定位用 `page.foreground/background`**；`place(scope: "parent", float: true)` 跳出分栏；非浮动 place 覆盖式不占流但调用点可能断段。

### 任务 14 — cjk.typ（CJK）
- 候选升级为**原生方案**：`font: (name: "…", covers: "latin-in-cjk")` 分字体描述符 + `text.cjk-latin-spacing`（CJK 与拉丁自动间距）——比 ctyp 正则 hack 更原生；ctyp 作 fallback。
- 实测：`\p{Han}` Unicode 正则可用；show-regex set font 与 `text(size:)` 缩放兼容（expA：混合文本行高 = CJK 高 ×1.1 精确）。
- 标点悬挂/压缩**无原生支持**（依赖字体 OpenType 特性）→ spike。

### 任务 17 — overflow.py（2026-08-07 调研修正，重要）
- **弃用 edwinhu 锚点页差法**：帧内溢出不改变页码 → 锚点页差检测不到，**不可用**（调研结论）。
- **采用 measure 对比模式**：模板内 `measure(body, width: W).height` vs 帧高 H → fill/deficit 写 metadata + label；进程侧 `typst eval 'query(metadata)'` 全量取回（**含 label 字段**，expB 实证）→ Python 按 label 分组 → demand.json。
- **防不可断长词假阴性（双测法）**：① 无约束 `measure(text).width` 得自然宽 W；② 约束 `measure(width: W₀, text).height` 得高 H。若 W > W₀ 且 H 单行 → 不可断行溢出，判 overflow。
- **query 触发多遍编译**（文档：自影响查询 5 次放弃）→ 控制查询量；0.15 有布局不收敛详细诊断可当 CI 报警器。

### 任务 19/20 — 测试与 CI
- 测试数量**以 linotype 实际 14 个测试函数为基**迁移 + 新增（非计划早期写的 25/28）。
- CI：`typst` CLI + Python 绑定 `typst`（**锁 Python 3.12/3.13**——3.14 无 wheel + PEP 668）；移除 texlive-xetex。

## 四、风险登记更新

### 已解除（调研实证）
| 风险 | 解除证据 |
|---|---|
| framefit 缩放 × CJK 字体切换 | expA：字号缩放穿透字体切换（8.82 = 8.02×1.1） |
| typst eval 批量多 label 查询 | expB：`query(metadata)` 全量 + label 字段 |
| framefit 字号缩放 vs 公式固定字号（U3） | expH2/5：show-set 锁公式免疫缩放 |
| #7779 阻断高度量测 | P0 exp4 + expD + 代理实测：约束宽下高度正确 |
| framefit 需联网下载 | expE：拉取成功（6.2 KiB） |

### 新增/调整（保留）
| 风险 | 级别 | 缓解 |
|---|---|---|
| 多遍编译对 presswire 大文档性能 | 🟠 | 控制查询量；避免自影响查询 |
| columns() 内容分配与溢出未文档化 | 🟠 | 任务 8 起步 spike（固定块内 columns） |
| 画报 place 在 layout 回调内未验证 | 🟠 | 任务 13 mini-spike；整页定位用 page.foreground/background |
| 标点悬挂/压缩无原生支持 | 🟡 | 任务 14 spike（字体 OpenType 特性） |
| typst-py 是否暴露 query API | 🟡 | 任务 17 spike；不行退回子进程 eval |
| 0.15 基线信息保留（box/block 对齐变化） | 🟡 | 回归比对 0.14 |

### 实测发现的重要陷阱
- **measure 无约束时对嵌套 text 元素测量异常**（宽度离谱/高度误判，expH1/H3）——**有宽度约束时正常**（expH4）→ presswire 一律带 `width: W`。
- **内层 `text(size:)` 锁字号**：对文本生效（expH4），对公式无效（expH6）——U3 必须用 show-set。

## 五、UAT 编号修正
- 原计划 U5 重复 → **U7 视觉等价**（pixelcheck 0 FAIL）。

## 六、复用清单变更摘要
（完整清单见编排层计划；此处记录调研新增/变更）
- **新增直接依赖**：`cjk-unshrink`（全角标点防压缩）、`cjk-spacer`（公式 CJK 间距）、`gridlock`（跨栏基线，评估）。
- **升级为直接依赖**：`one-liner`（autofit 初值）。
- **借算法变更**：edwinhu overflow.py 仅借 JSON→fill/deficit 结构（通道改 eval；且**页差法弃用**，任务 17 用 measure 对比）；新增 dashing-dept-news `state()` 收集器（任务 8 栏模板起点）。
- **避雷补充**：LiX（GPL-3.0+LaTeX）、zine（HTML 非分页）、latex-newspaper-rjldtp（AGPL，仅借算法思想）。

## 七、版本锁定
- typst **0.15.1**（实测版本）；CI 用 `typst compile` + `typst eval` 双命令。
- 保留升级回归用例（0.11→0.15 breaking 清单见 `dev/research/philosophy/typst-philosophy-report.md` 第五节；未来 0.16 需再查 changelog）。
