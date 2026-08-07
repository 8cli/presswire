import typst, json

# 1. 编译 → PDF bytes
pdf = typst.compile("presswire-style.typ")
print(f"1. compile OK, PDF {len(pdf)} bytes")

# 2. eval 全量取 metadata（任务 17 核心）
raw = typst.eval("presswire-style.typ", "query(metadata)")
vals = json.loads(raw)
print(f"2. eval query(metadata) → {len(vals)} 个元素")
for v in vals:
    print(f"   label={v.get('label')} value={v.get('value')}")

# 3. eval 单 label 取 value（P0 通路）
raw2 = typst.eval("presswire-style.typ", "query(<plate-P2>).first().value")
print(f"3. eval query(<plate-P2>).first().value → {raw2}")

# 4. query API（CLI query 对应）
raw3 = typst.query("presswire-style.typ", "<plate-P2>", field="value", one=True)
print(f"4. query(<plate-P2>, field=value, one=True) → {raw3}")
