"""contracts.py — demand.json / layout.json 字节级契约（任务 6）

移植 latin build.py 的输出结构（D2 红线: imposer 契约二进制兼容）:
- layout.json:  build.py:331-351（write_tex 的 JSON 部分）
- demand.json:  build.py:650-711（write_demand + estimate_requests）

数据来源演进（presswire 与 latin 的差异点，不影响结构）:
- latin 的 fill/deficit 从编译日志正则解析；presswire 从任务 7/17 的
  measure + metadata 通道得来（`typst eval 'query(metadata)'`）。
  本模块只定义结构与纯函数（estimate_requests），fill/deficit 由调用方传入。

用法（任务 16 cli 接入后）:
    layout = contracts.layout_json(layouts, docopts)     # → {'sheets':..., 'layout':...}
    demand = contracts.build_demand(plates_fill, fill_min)  # → {'plates':{...}} 或 None
"""
import json
import os

__all__ = ['layout_json', 'write_layout_json', 'estimate_requests', 'build_demand',
           'write_demand_json', 'TOPIC_BY_PLATE', 'MIN_KIND_BY_PLATE']

# 规格映射（与 latin build.py:651-652 一致）
TOPIC_BY_PLATE = {0: "world/military", 1: "ai/tech", 2: "space", 3: "tech"}
MIN_KIND_BY_PLATE = {0: "independent", 1: "company", 2: "agency", 3: "tech-media"}

# 默认太空容忍下界（--docopts fill_min= 覆盖；与 latin FILL_MIN 一致）
FILL_MIN = 0.95


def parse_docopts(docopts: str) -> dict:
    """解析 docopts 字符串 → dict（latin build.py:270-282 移植）。"""
    d = {}
    for part in docopts.split(','):
        part = part.strip()
        if not part:
            continue
        if '=' in part:
            k, v = part.split('=', 1)
            d[k.strip()] = v.strip()
        else:
            d[part] = True
    return d


# ---------- layout.json ----------

def layout_json(layouts: dict, docopts: str = '') -> dict:
    """组装 layout.json 结构（latin build.py:341-348 移植）。

    `layouts`: {p1: 'multi'|'single', ...}（render_typst.generate_typ 产出）。
    `docopts`: plates=2 且 ≥4 版 → 按页分 front/back（每页两版并排）；
               否则全塞 front。
    """
    opts = parse_docopts(docopts)
    dual = opts.get('plates') == '2'
    plates = list(layouts.keys())
    if dual and len(plates) >= 4:
        sheets = {'front': plates[:2], 'back': plates[2:]}
    else:
        sheets = {'front': plates}
    return {'sheets': sheets, 'layout': layouts}


def write_layout_json(out_dir: str, layouts: dict, docopts: str = '') -> str:
    """写 layout.json 到 out_dir，返回路径。"""
    path = os.path.join(out_dir, 'layout.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(layout_json(layouts, docopts), f, ensure_ascii=False, indent=1)
    return path


# ---------- demand.json ----------

def estimate_requests(fill: float, content_h: float, plate_idx: int,
                      fill_min: float = FILL_MIN) -> list:
    """按 fill 缺口估算补稿需求（latin build.py:655-675 移植，纯函数）。

    规格: type/words/min_kind/topic。fill ≥ fill_min 不发单。
    """
    if fill >= fill_min:
        return []
    deficit = (fill_min - fill) * content_h
    topic = TOPIC_BY_PLATE.get(plate_idx, "world")
    min_kind = MIN_KIND_BY_PLATE.get(plate_idx, "china-official")
    # 估算: 简讯 60-90 字 ≈ 26-40pt; 中篇 250-400 字 ≈ 110-175pt; 深度 400-600 字 ≈ 175-260pt
    if deficit < 100:
        return [{"type": "brief", "count": max(1, int(deficit // 33)), "words": [60, 90],
                 "topic": topic, "min_kind": min_kind}]
    if deficit < 300:
        return [{"type": "main", "count": 1, "words": [250, 400], "topic": topic, "min_kind": min_kind},
                {"type": "brief", "count": max(1, int((deficit - 140) // 33)), "words": [60, 90],
                 "topic": topic, "min_kind": min_kind}]
    return [{"type": "deep_dive", "count": 1, "words": [400, 600], "topic": topic, "min_kind": "thinktank"},
            {"type": "brief", "count": max(1, int((deficit - 200) // 33)), "words": [60, 90],
             "topic": topic, "min_kind": min_kind}]


def build_demand(plates_fill: dict, fill_min: float = FILL_MIN) -> dict | None:
    """从每版 fill/deficit 组装 demand.json 结构（latin build.py:697-706 移植）。

    `plates_fill`: {"P1": {"fill": 0.31, "deficit_pt": 84.2}, ...}
                   —— presswire 数据来源: 任务 7/17 measure + metadata 通道
                   （latin 从编译日志解析）。键必须带 "P" 前缀（P1, P2, ...）。
    返回 {"plates": {...}}；无需求（全部达标）→ None。
    """
    plates = {}
    for pid, pf in sorted(plates_fill.items()):
        # plate_idx 由版编号推导（P3 → 2），等价 latin 日志顺序枚举
        idx = int(pid[1:]) - 1
        fill = pf.get('fill', 1.0)
        content_h = pf.get('deficit_pt', 0) / max(fill_min - fill, 1e-9) if fill < fill_min else 0
        reqs = estimate_requests(fill, content_h, idx, fill_min)
        if reqs:
            deficit_pt = pf.get('deficit_pt')
            if deficit_pt is None:
                deficit_pt = round((fill_min - fill) * content_h, 1)
            plates[pid] = {"fill": round(fill, 3),
                           "deficit_pt": deficit_pt,
                           "requests": reqs}
    if not plates:
        return None
    return {"plates": plates}


def write_demand_json(out_dir: str, plates_fill: dict, fill_min: float = FILL_MIN) -> str | None:
    """写 demand.json 到 out_dir，返回路径；无需求 → None。

    与 latin write_demand 的"无需求清空旧单"语义对应：调用方在返回 None
    时删除旧 demand.json（血泪 #53）。
    """
    demand = build_demand(plates_fill, fill_min)
    if demand is None:
        return None
    path = os.path.join(out_dir, 'demand.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(demand, f, ensure_ascii=False, indent=2)
    return path


if __name__ == '__main__':
    # 自测: 与 latin 结构对照
    layouts = {'p1': 'single', 'p2': 'multi', 'p3': 'single', 'p4': 'single'}
    print('layout(单版):', layout_json(layouts))
    print('layout(双版):', layout_json(layouts, 'paper=a3,plates=2'))
    print('demand:', build_demand({'P1': {'fill': 0.91, 'deficit_pt': 12.0},
                                   'P3': {'fill': 0.31, 'deficit_pt': 84.2}}))
    print('demand(全达标):', build_demand({'P1': {'fill': 0.97, 'deficit_pt': 0.0}}))
