# 实验 B — typst eval 批量多 label 查询

> 日期：2026-08-07 · Typst 0.15.1 · 源文件：`expB-batch-query.typ`
> 登记风险 #1（eval 多 label 批量查询的 JSON 结构）

## 问题

P0 验证了单 label 查询 `typst eval 'query(<plate-id>)'` 返回完整 value。但报纸 4 版需要**一次取回全部** fill/deficit——多 label 批量查询的 JSON 结构是什么？

## 方法

构造 4 组 `#metadata((plate, fill, deficit, overflow))` + 相邻 `#label("plate-PN")`，测试 4 种查询方式。

## 结果

| 查询方式 | 结果 |
|---|---|
| `query(<plate-P2>)`（单 label） | ✅ 完整 value：`{"plate":"P2","fill":0.72,"deficit":"30.5pt","overflow":true}`，label 字段 `<plate-P2>` |
| `query(label)`（selector） | ❌ **非法**：`error: only element functions can be used as selectors` |
| `query(metadata).map(e => e.value.plate)` | ✅ 全量 4 个：`["P1","P2","P3","P4"]` |
| `query(metadata).filter(e => e.label == <plate-P2>).map(e => e.value)` | ✅ 按 label 过滤可取单版 value |

**关键**：`query(metadata)` 返回的每个元素**带 `label` 字段**（`{"func":"metadata","value":{...},"label":"<plate-P2>"}`），所以**批量 = `query(metadata)` 全量取回 + Python 侧按 label 分组**，无需逐个 label 查询。

## 结论

✅ **风险 #1 基本解除**：批量查询用 `query(metadata)` 一次取回全部 metadata（含 label 字段），Python 侧 `json.loads` 后按 `label` 分组。单版查询仍可用 `query(<label>)`。

## 对 presswire 的建议

- 任务 17（overflow.py）：`typst eval 'query(metadata)' --format json` → Python 按 label 提取各版 fill/deficit/overflow → 聚合 demand.json。
- `query(label)` 作为 selector 非法（label 不是元素函数）——不要用它做批量。
- metadata 的 `deficit` 长度字段 JSON 序列化为**字符串**（`"30.5pt"`）——Python 侧需 `float(x.replace("pt",""))`（P0 已记录，此实验再次确认）。
