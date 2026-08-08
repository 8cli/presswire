"""overflow.py — 溢出报告读取 + demand 组装（任务 17）

measure 对比模式（2026-08-07 调研修正——edwinhu 锚点页差法对固定版心无效:
帧内溢出不改变页码，检测不到）:
  模板内 plate-frame（plate.typ）: `measure(body, width: W).height` vs 帧高 H
  → fill/deficit/overflow 写 metadata + 相邻 label；本模块进程侧
  `typst eval 'query(metadata)'` 全量取回（含 label 字段，expB 实证）→
  Python 按 label 分组 → demand.json（contracts.build_demand）。

双测法（不可断长词假阴性）: ① 无约束 measure(text).width 得自然宽 W；
  ② 约束 measure(width: W₀, text).height 得高 H。若 W > W₀ 且 H 单行 →
  不可断行溢出（宽度溢出）。实测（2026-08-08）: 长词 237pt > 约束 100pt
  单行 → 判定成立。注: 对整体 body 不可用（长文本自然宽必然超版心——
  折行语义）；适用于文本字段级检测（标题/段落长词）。

query 触发多遍编译（文档: 自影响查询 5 次放弃）→ 控制查询量；
本模块每次调用一次 eval（全量取回），不逐 label 查询。
"""
import json
import os
import subprocess

from . import contracts

TYPST_CLI = os.environ.get('TYPST', '/usr/local/bin/typst')


def parse_fills(metadata_list: list) -> dict:
    """metadata 元素列表 → {plate-PN: {fill, deficit_pt, overflow}}（双后端共用）。

    `metadata_list`: query(metadata) 结果（CLI eval JSON 或 typst-py eval
    解析后的 list）。deficit_pt 为字符串（"341.18pt"）→ 转 float。
    """
    out = {}
    for el in metadata_list:
        label = el.get('label', '')
        v = el.get('value', {})
        pid = label.strip('<>') if label else v.get('plate', '?')
        deficit = v.get('deficit_pt', '0pt')
        out[pid] = {
            'fill': v.get('fill', 0.0),
            'deficit_pt': round(float(str(deficit).replace('pt', '')), 1),
            'overflow': v.get('overflow', False),
        }
    return out


def read_fills(typ_path: str, root: str) -> dict:
    """eval query(metadata) → {plate-PN: {fill, deficit_pt, overflow}}。

    `root`: --root 参数（模板资产沙箱；cli 传 REPO_ROOT）。
    """
    r = subprocess.run([TYPST_CLI, 'eval', '--root', root,
                        'query(metadata)', '--in', typ_path,
                        '--format', 'json'], capture_output=True, text=True)
    if r.returncode != 0:
        return {}
    return parse_fills(json.loads(r.stdout))


def plates_fill_demand(fills: dict) -> dict:
    """{plate-PN: fill 报告} → contracts.build_demand 输入（deficit_pt 契约换算）。

    plate-frame 报告的 deficit = (1 − fill) × content_h；latin demand 契约
    deficit_pt = (fill_min − fill) × content_h → 反推 content_h 后换算。
    """
    plates = {}
    for pid, f in fills.items():
        pnum = pid.replace('plate-P', 'P')
        if f['fill'] < 1:
            content_h = f['deficit_pt'] / (1 - f['fill'])
        else:
            content_h = 0
        deficit = round((contracts.FILL_MIN - f['fill']) * content_h, 1) \
            if f['fill'] < contracts.FILL_MIN else 0.0
        plates[pnum] = {'fill': f['fill'], 'deficit_pt': deficit}
    return plates
