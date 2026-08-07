<div align="center">

# 🗞️ Presswire

**A Typst-based newspaper typesetting engine — behavior-compatible with Linotype**

把 Markdown 内容排成可印刷的多栏 PDF，带编译期溢出检测。

`plates/*.md` → `build.py` → `typst` → **PDF**

[快速开始](#quick-start) · [内容格式](#content-format) · [配置](#configuration) · [QA 流水线](#qa-pipeline) · [English Summary](#english-summary)

</div>

---

## 这是什么？

**Presswire** 是基于 [Typst](https://typst.app) 的**通用配置驱动排版引擎**，行为等价于 [Linotype](https://github.com/8cli/linotype)（LaTeX 版）。它不绑定任何具体报刊：给它任意一组 Markdown plates，选定纸张尺寸、栏数、字体与配色主题，即可产出印刷级 PDF。

核心差异点是**固定视口排版**：内容被排入固定内容区（"plate"），若内容超出版面，页面**不会**推到下一页——溢出以编译期警告报告（`Overfull plate: content Xpt > contentH Ypt`），版面保持稳定。

> 现有的报纸排版项目（LaTeX 系 Linotype 之外，Typst 生态尚无等价物）都允许溢出内容推到新页或静默越界。Presswire 是唯一在编译期精确报告超出多少的 Typst 引擎。

## 能力

- **中英混排（CJK 真支持）**：同一 plates 含中文 + 英文段落正确排版，中文标点、混排基线正常
- **数学公式**：主体/版内 `$...$` 内联与块级公式用 Typst 原生语法正确渲染，不破坏 autofit/版面
- **画报排版**：`LAYOUT: poster` 产出画报 PDF（图片主导/网格排布）
- **契约兼容**：`cli.py` 与 `build.py` 输入输出契约与 linotype 字节一致（plates 解析 + `--docopts`/`--visual`/`--demand` + demand.json 与 layout.json 结构）
- **固定视口 + 溢出检测**：`#measure` 各版体高度，折算 fill/溢出量写 `#metadata(...)`，溢出时 panic（退出码非 0）
- **autofit-in-typst**：用 `framefit` 对主正文字号做二分 measure 收敛，单次 `typst compile` 完成（无 `\@colht` hack、可变字体原生）

## Quick Start

```bash
# 1. 创作内容 —— 每个 plate 一个 Markdown 文件（见 examples/plates/）
ls examples/plates/

# 2. 从 plates 生成 Typst 数据文本
python3 build.py examples/plates/ examples/sample.typ \
    --docopts "paper=a3,landscape,columns=3,plates=1"

# 3. 编译
typst compile examples/sample.typ

# 4. 后处理 QA
python3 pdfcheck.py examples/sample.pdf --paper a3 --landscape --pages 2
```

## Content Format

每个 plate 是 `plates/pN.md` 文件，带**字段标签**（非 Markdown 标题）：

```markdown
LAYOUT: main-aside        # 可选：''（等宽多栏，默认）| main-aside | poster
COLUMNS: 3                # 可选：单版栏数
EXPANDEDTITLE: Title      # 可选：跨栏通栏标题
IMAGE: img.jpg            # 可选：图片路径
IMAGEWIDTH: 1.0           # 可选：图片宽度占版面比例 0-1（默认 1.0）
IMAGECAPTION: Caption     # 可选：图片说明
KICKER: Section label
HEADLINE: Main headline
SUBHEADLINE: Subtitle     # 可选
DECK: Standfirst
BYLINE: Byline
BODY:                     # 正文段落，空行分隔
First paragraph...
Second paragraph...
STORY-B: Sidebar title    # 可选，main-aside 版式
Sidebar body...
PULLQUOTE: Quote          # 可选
BRIEFS:                   # 可选，最多 3 条
**Item 1:** text...
```

**字段参考：**

| 字段 | 位置 | 含义 |
|---|---|---|
| `LAYOUT` | 头部 | `main-aside` = 主栏 2 列 + 侧栏 1 列；`poster` = 画报；默认等宽多栏 |
| `COLUMNS` | 头部 | 单版栏数（覆盖 `--docopts` 全局值） |
| `EXPANDEDTITLE` | 头部 | 跨全部栏的通栏标题 |
| `IMAGE` / `IMAGEWIDTH` / `IMAGECAPTION` | 头部 | 版顶图（图片高度计入溢出检测） |
| `KICKER` / `HEADLINE` / `SUBHEADLINE` / `DECK` / `BYLINE` | 头部 | 报道标题链 |
| `BODY` | 区块 | 正文段落，空行分隔 |
| `STORY-B` / `STORY-C` | 区块 | 侧栏/附栏报道（main-aside 版式） |
| `PULLQUOTE` | 头部 | 引语框 |
| `BRIEFS` | 区块 | "简讯"条目（最多 3 条） |

特殊字符（Typst 转义：`` ` ``、`$`、`<`、`>` 等）由 `build.py` 自动处理。

## Configuration

### `--docopts` 键（对应 linotype 的 `\linotypesetup`）

| 键 | 取值 | 默认 | 说明 |
|---|---|---|---|
| `paper` | `a3` / `a4` / `letter` | `a3` | 纸张尺寸 |
| `landscape` / `portrait` | — | portrait | 方向 |
| `columns` | 2–4 | 3 | 全局栏数 |
| `plates` | 1 / 2 | 2 | 每页版数（2 = 并排） |
| `theme` | `broadsheet` / `magazine` | `broadsheet` | 主题预设（字体 + 配色） |
| `bodyfontsize` | 长度 | `9.5pt` | 正文基字号——autofit 旋钮；所有原子按比例缩放 |
| `ink` / `accent` / `papercolor` | hex | `1A1A1A` / `8C1D18` / `FFFFFF` | 颜色 |

### `build.py` CLI 参考

```
python3 build.py <plates_dir> <output.typ> [options]

positional:
  plates_dir    存放 plates/pN.md 的目录
  output        输出 .typ 路径（autofit 模式下另产出 .pdf + .log）

options:
  --docopts "paper=a3,landscape,columns=3,plates=1"   排版键（逗号分隔）
  --theme magazine        主题预设
  --no-autofit            仅生成 .typ，不编译不搜索
  --visual                autofit 后渲染 PDF → 像素诊断 → 修复建议
  --demand                输出 demand.json 补白请求
```

## QA Pipeline

排版即**带警告的构建**：

| 阶段 | 工具 | 检测 | 失败条件 |
|---|---|---|---|
| autofit | `build.py` 循环 | 收敛（0 Overfull，min fill ≥ 45%） | 内容无法装入 → 最优尝试报告 |
| 编译 | `typst` + 模板 | `Overfull plate: content Xpt > contentH Ypt` | 内容超出固定视口 |
| 编译 | `metadata` / `typst query` | fill / deficit 量 | 溢出 panic（退出码非 0） |
| 后处理 | `pdfcheck.py` | 页数、字体、MediaBox | 任何不符 |
| 视觉 | `pixelcheck.py` | 栏间隙 / 底部溢出 | 生产页出现空白带 |

```bash
# 回归套件（正负矩阵，临时目录运行）
python3 tests/run_tests.py /path/to/engine
```

## English Summary

**Presswire** is a configuration-driven newspaper typesetting engine built on **Typst**, behaviorally equivalent to Linotype (the LaTeX engine). It turns `plates/*.md` content into print-quality multi-column PDFs with compile-time overflow detection — the page never pushes when content overflows a fixed plate; instead it reports exactly how much room was exceeded.

Its distinctive capabilities over the LaTeX original:

- **True CJK support** — Chinese + English mixed typesetting in the same plate, correct punctuation and baseline
- **Native math** — Typst `$...$` inline/block formulas, font size fixed (not scaled by the autofit knob)
- **Poster layouts** — `LAYOUT: poster` for image-led pictorial pages
- **Contract compatibility** — same `build.py` / `cli.py` input-output contract as Linotype (plates parsing, `--docopts`/`--visual`/`--demand`, demand.json/layout.json structures)
- **Autofit in Typst** — binary-search font convergence in a single `typst compile` (no LaTeX hacks; variable fonts natively)

## 项目布局

```
├── presswire.typ         # Typst 基础模板（page + 逐版排版 + 空"权威"嵌入）
├── plate.typ             # 固定高度内容盒 + 溢出 clip + metadata 报告
├── autofit.typ           # framefit 二分 measure 收敛
├── build.py              # 内容流水线：plates → .typ + layout.json
├── pdfcheck.py           # PDF 后处理 QA
├── SKILL.md              # Claude Code skill 手册（agent 面向）
├── examples/
│   └── plates/           # 示例内容（全部字段格式）
├── scripts/
│   └── ci-install-fonts.sh  # 静态字体安装（含 Noto Sans/Serif SC）
└── tests/
    └── run_tests.py      # 正负回归矩阵
```

## 文档与调研

| 文档 | 说明 |
|---|---|
| [docs/comparison-linotype.md](docs/comparison-linotype.md) | presswire vs linotype 全面评估（契约层相同 + 内核层差异） |
| [docs/plan-revisions.md](docs/plan-revisions.md) | 计划修订与决策记录（P0 结论 / U3 定案 / 任务 17 修正 / 风险登记） |
| [dev/research/README.md](dev/research/README.md) | 开发难点调研索引（风险矩阵 + 交叉验证） |
| [dev/research/philosophy/](dev/research/philosophy/) | Typst 哲学与避坑指南（17 坑 / 版本注意 / 官方文档研究） |
| [dev/research/experiments/](dev/research/experiments/) | 9 组本地实测（typst 0.15.1 实证：measure/CJK/framefit/U3） |

## License

[MIT](LICENSE) © 2026 Yu (8cli)
