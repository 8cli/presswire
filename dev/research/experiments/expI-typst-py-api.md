# 实验 I — typst-py query/eval API 验证（任务 17 关键）

> 日期：2026-08-07 · 来源：messense/typst-py README + 源码（src/query.rs）+ GitHub API
> 目的：验证 presswire 唯一"未验证"的集成点——Python 进程内能否直接跑 query/eval（免子进程调 CLI）

## 结论（✅ 已验证）

**typst-py 完整暴露 `compile` / `query` / `eval` 三 API + `Compiler` 类**——任务 17 可**进程内**查询，无需子进程调 `typst eval` CLI。

## 已验证的 API（README 原文）

```python
import typst

# 编译
pdf_bytes = typst.compile("hello.typ")                        # 返回 bytes
typst.compile("hello.typ", output="hello.pdf", format="png", ppi=144.0)
typst.compile(input, output, sys_inputs=sys_inputs, pretty=True, timestamp=...)

# 查询（对应 CLI query；field 抽字段, one 期望唯一）
values = json.loads(typst.query("hello.typ", "<note>", field="value", one=True))

# 求值（对应 CLI eval；Typst 0.15 的新方式）
values = json.loads(typst.eval("hello.typ", "query(<note>).first().value"))

# 编译器类（避免重复初始化, 多文件复用）
compiler = typst.Compiler()
compiler.compile(input="hello.typ", format="png", ppi=144.0)
```

## 源码确认（src/query.rs）

- `QueryCommand { selector: String, field: Option<String>, one: bool, format: Json|Yaml }`
- `EvalCommand { expression: String, format, pretty }`
- `query()` 内部 = `typst::compile(world)` → `retrieve` → 序列化（**与 CLI query 同一实现路径**）
- `eval()` 内部 = `typst::compile::<PagedDocument>` → `evaluate`（**用 document.introspector()** → 正是 typst eval 的语义：先编译再在文档上下文中求值表达式）
- **关键**：`query`/`eval` 都是先完整编译文档，再处理查询——与 CLI 行为一致（含多遍编译特性）。

## 多文件项目（README）

- 传字典 `{文件名: bytes}`，入口键必须为 `"main"` 或 `"main.typ"`（单文件任意键）。
- `sys_inputs` 支持传 `--input key=value` 类参数。

## 对 presswire 任务 17 的影响（升级方案）

**原方案**：子进程调 `typst eval 'query(metadata)' --in doc.typ --format json`。
**升级方案（已验证可用）**：
```python
import typst, json
values = json.loads(typst.eval("out.typ", "query(metadata)"))
# → [{"func":"metadata","value":{...},"label":"<plate-P2>"}, ...]
# Python 侧按 label 分组 → demand.json
```
- 优点：进程内（无子进程开销/路径参数传递）、跨平台、错误在 Python 内可捕获。
- **要求**：Python 3.12/3.13（typst 0.15.0 wheel 无 3.14）→ 与 CI/venv 环境约束一致（已在计划任务 2 注明）。
- 降级路径：若环境装不了 typst-py（如纯 3.14 无 venv），退回子进程 `typst eval`（CLI 0.15.1 已装，P0 已验证此路径同样可行）——**两条路都通**。

## 风险登记更新

- ✅ **解除**：~~typst-py 是否暴露 query API~~ → 已验证暴露 query + eval（本次）。
- 新增确认：`typst.query(..., one=True)` 返回 JSON 字符串（需 `json.loads`）；`field="value"` 直接抽字段——对应 P0 的 `query(<label>).first().value`。
