import typst
try:
    typst.compile("panic.typ")
    print("compile 返回(无异常) — 未捕获 panic")
except typst.TypstError as e:
    print("捕获 TypstError:", str(e)[:100])
except Exception as e:
    print("捕获其他异常:", type(e).__name__, str(e)[:100])
# 且: 即使 panic, eval 仍能读 metadata?
try:
    raw = typst.eval("panic.typ", "query(metadata)")
    print("eval 仍工作:", raw[:120])
except Exception as e:
    print("eval 失败:", str(e)[:100])
