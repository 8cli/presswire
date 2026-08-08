#!/usr/bin/env python3
"""expS — typst-py 内存通讯三实验（盲区 1/2/4）

实验1 (panic 消息): 长文 plates autofit → TypstError.message 是否含
    'content does not fit'（与 CLI stderr 逐字一致？）
实验2 (--root 等价): compile(input=out.typ, root=~/news) 日报场景能否
    解析 ../presswire_typst/presswire.typ（跨目录模板资产）
实验4 (内存释放): 同一进程连续 compile 5 次，观察 RSS 是否增长
"""
import os, sys, time, json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))  # presswire repo root
from presswire.render_typst import generate_typ

REPO = Path.home() / 'news' / 'presswire'
LATIN_PLATES = Path.home() / 'news' / 'latex' / 'examples' / 'plates'   # 长文 12% 溢出
FIXTURES = REPO / 'tests' / 'fixtures' / 'layouts'                      # 短内容

def gen(name: str, plates_dir, autofit: bool) -> Path:
    text, _ = generate_typ(str(plates_dir))
    p = REPO / f'expS-{name}.typ'
    p.write_text(text.replace('#render-doc(plates)',
                 f'#render-doc(plates, autofit: {"true" if autofit else "false"})'), encoding='utf-8')
    return p

def rss_kb():
    with open('/proc/self/status') as f:
        for line in f:
            if line.startswith('VmRSS:'):
                return int(line.split()[1])
    return 0

print('=== 实验1: panic 消息一致性 ===')
import typst
typ = gen('overflow', LATIN_PLATES, autofit=True)
try:
    typst.compile(str(typ), output=str(typ.with_suffix('.pdf')), root=str(REPO))
    print('FAIL: 长文 autofit 应 panic 却成功')
except Exception as e:
    print(f'异常类型: {type(e).__name__}')
    print(f'完整 str: {e}')
    print(f'含 content does not fit: {"content does not fit" in str(e)}')
    # 尝试访问 .message
    for attr in ('message', 'args', 'msg'):
        if hasattr(e, attr):
            v = getattr(e, attr)
            print(f'.{attr}: {v if isinstance(v, str) else v}')

print()
print('=== 实验2: --root 等价（日报场景）===')
import tempfile, subprocess
# 模拟日报: out.typ 在 ~/news/daily/DATE/ 下, 模板在 ~/news/presswire/presswire_typst/,
# root=~/news（out.typ 用 ../presswire_typst/ 上溯）
DAILY = Path.home() / 'news' / 'daily' / 'expS-test'
DAILY.mkdir(parents=True, exist_ok=True)
text, layouts = generate_typ(str(FIXTURES))
# 模板相对路径: ~/news/presswire/presswire_typst/presswire.typ 相对 ~/news/daily/expS-test/
tpl_rel = os.path.relpath(REPO / 'presswire_typst' / 'presswire.typ', DAILY).replace(os.sep, '/')
text = text.split('#import "presswire_typst/presswire.typ": render-doc')[0] + \
       f'#import "{tpl_rel}": render-doc\n#render-doc(plates)\n'
out_typ = DAILY / 'out.typ'
out_typ.write_text(text, encoding='utf-8')
try:
    typst.compile(str(out_typ), output=str(DAILY / 'out.pdf'), root=str(Path.home() / 'news'))
    print(f'root=~/news 编译成功 → {DAILY / "out.pdf"} 存在: {(DAILY / "out.pdf").exists()}')
except Exception as e:
    print(f'FAIL: {type(e).__name__}: {e}')

print()
print('=== 实验4: 重复编译内存占用 ===')
def compile_ok(typ_path):
    typst.compile(typ_path, output=str(typ_path.with_suffix('.pdf')), root=str(REPO))
short = gen('short', FIXTURES, autofit=True)
compile_ok(short)  # 预热
rss_before = rss_kb()
for i in range(5):
    compile_ok(short)
    print(f'第{i+1}次编译后 RSS: {rss_kb()} kB')
rss_after = rss_kb()
print(f'增长: {rss_after - rss_before} kB')

# 清理
for name in ('overflow', 'short'):
    for suffix in ('.typ', '.pdf'):
        p = REPO / f'expS-{name}{suffix}'
        if p.exists(): p.unlink()
import shutil; shutil.rmtree(DAILY, ignore_errors=True)
print()
print('实验完成')
