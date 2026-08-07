# 实验 K — typst-py 端到端运行时验证（任务 17 完全实现）

> 日期：2026-08-07 · typst-py 0.15.0 · Python 3.12.13（uv venv）
> 前置：`expI-typst-py-api.md`（API 存在性验证，README+源码）→ 本实验**实际运行**

## 问题

expI 只读 README/源码验证了 API 存在。任务 17 需要**真实调用** `typst.eval("query(metadata)")` 进程内取回数据——未实测。

## 环境搭建（关键发现）

- 本机 Python 3.14.4 装不了 typst（无 wheel）。
- **用 uv 快速搭 3.12 venv**：`uv python install 3.12` + `uv venv --python 3.12` + `uv pip install typst` → **typst==0.15.0 安装成功**（~30 秒）。
- ✅ 这确认了 **CI/venv 用 Python 3.12/3.13 + typst-py 的完整可行路径**（计划任务 2/20 的环境约束验证通过）。

## 端到端实测（presswire 风格文档）

```python
import typst, json

# 1. 编译 → PDF bytes
pdf = typst.compile("presswire-style.typ")   # ✅ 2131 bytes

# 2. eval 全量取 metadata（任务 17 主通道）
raw = typst.eval("presswire-style.typ", "query(metadata)")
vals = json.loads(raw)   # ✅ 2 个元素, 含 label 字段
#   label=<plate-P1> value={'plate': 'P1', 'fill': 0.95, 'deficit': '0pt', ...}
#   label=<plate-P2> value={'plate': 'P2', 'fill': 0.72, 'deficit': '30.5pt', ...}

# 3. eval 单 label 取 value（P0 通路）
typst.eval(file, "query(<plate-P2>).first().value")   # ✅ 完整 dict

# 4. query API（CLI query 对应）
typst.query(file, "<plate-P2>", field="value", one=True)   # ✅ 抽字段
```

## 验证点全通过

| 通道 | 结果 | 用途 |
|---|---|---|
| `compile()` → bytes | ✅ | 无文件输出编译（CI 内嵌） |
| `eval(file, "query(metadata)")` | ✅ 全量 + label | **任务 17 主通道**（按 label 分组 → demand.json） |
| `eval(file, "query(<label>).first().value")` | ✅ 单版 value | P0 通路的进程内版 |
| `query(file, "<label>", field="value", one=True)` | ✅ 抽字段 | 快速单字段 |

## 关键确认

1. **metadata 长度字段 JSON 字符串化**再次实证：`deficit: '30.5pt'` → Python 需 `float(x.replace("pt",""))`。
2. **进程内通道完全可用**——无需子进程调 CLI，错误在 Python 内可捕获（TypstError/TypstWarning 类）。
3. **环境约束验证**：uv + Python 3.12 + typst-py 0.15.0 全链路可用（CI 的 venv 方案照此）。

## 对 presswire 任务 17 的最终方案

```python
# overflow.py 核心（进程内）
import typst, json

def read_fills(typ_file: str) -> dict:
    raw = typst.eval(typ_file, "query(metadata)")
    out = {}
    for el in json.loads(raw):
        label = el.get("label", "")            # "<plate-P1>"
        value = el.get("value", {})
        pid = label.strip("<>") if label else value.get("plate", "?")
        out[pid] = {
            "fill": value.get("fill"),
            "deficit": float(str(value.get("deficit", "0pt")).replace("pt", "")),
            "overflow": value.get("overflow"),
        }
    return out
```

（模板侧：`#metadata((fill: ..., deficit: ..., overflow: ...)) #label("<plate-PN>")`——P0/expB 已定。）
