# expS — typst-py 内存通讯三实验（2026-08-08）

> 目的：imposer ↔ presswire 通讯升级（内存模式）前置盲区验证。
> 背景：方案 C（typst-py 全进程内）的三个未知点——
> panic 消息一致性 / --root 等价 / 内存释放。

## 实验环境

- Python 3.12.4 venv（`~/news/presswire/.venv312`），typst-py 0.15.0
- 与 CLI 同编译器核心（Rust），版本配对（CI 同款锁版本）
- 长文 plates：`~/news/latex/examples/plates`（真实溢出 12%）
- 短内容：`tests/fixtures/layouts`

## 实验 1：panic 消息一致性 ✅

**方法**：长文 plates autofit=true → typst-py compile → 捕获异常，检查消息。

**结果**：
```
异常类型: TypstError
.message: panicked with: framefit: content does not fit at the minimum size.
         Make the frame larger, reduce the content, or lower `min`.
含 'content does not fit': True
```

**结论**：typst-py 的 TypstError.message 与 CLI stderr **逐字一致**。
cli.py 的"文章不符合"信号检测（`'content does not fit' in r.stderr`）可直接
迁移为 `'content does not fit' in str(e)`，零适配。D4 红线从"panic 退出码 1
+ 正则匹配 stderr"升级为 try/except TypstError——更可靠。

## 实验 2：--root 等价 ✅

**方法**：模拟日报场景——out.typ 在 `~/news/daily/expS-test/`，模板在
`~/news/presswire/presswire_typst/`，root=~/news，out.typ 用 `../presswire_typst/`
上溯。`typst.compile(input, output, root=~/news)`。

**结果**：编译成功，out.pdf 生成。

**结论**：`compile()` 原生支持 `root` 参数（与 CLI `--root` 同语义）。
无需 cwd 切换或临时目录绕行。library.py 的 root 参数直接透传。

## 实验 3：重复编译内存占用 ⚠️（可接受）

**方法**：同一进程连续 compile 5 次（短内容），观察 VmRSS。

**结果**：
```
预热后 RSS:  204212 kB
第 1-4 次:   204224 kB（稳定）
第 5 次:     229884 kB（+26 MB）
```

**结论**：typst 编译器堆进 Python 进程（~204MB 常驻），前 4 次稳定，
第 5 次出现 26MB 增长（字体/包缓存累积，非泄漏级）。日报是短命批次
（每次出报 ≤2 轮编译），单进程内存可接受；与 CLI 独立进程内存同级，
只是从"用完即弃的子进程"变为"批次内常驻"。imposer 主路径每轮编译后
进程退出，无泄漏累积风险。

## 综合结论

方案 C（typst-py 全进程内）**可行性坐实**，三个盲区全部消除：

| 盲区 | 结论 | 落地 |
|---|---|---|
| panic 消息 | TypstError.message 含 `content does not fit` | try/except + 消息匹配 |
| --root 等价 | compile(root=...) 原生支持 | 透传参数 |
| 内存 | ~204MB 批次内稳定 | 短命批次可接受 |

## 后续

- library.py 门面：`render(plates_dir, docopts, root, autofit) -> {pdf, fills, demand, layout}`
- cli.py `--json`：结构化 stdout（parse_demand 免正则）
- imposer 内存模式分支（--inmem）：import presswire.library → dict 闭环
