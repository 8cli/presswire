#!/usr/bin/env bash
# presswire CI 字体安装: 从 google/fonts 拉取可变字体 → fonttools instancer 生成静态实例 → fc-cache
#
# 迁移自 latex/scripts/ci-install-fonts.sh（保持逻辑骨架，改字体清单）。
# 背景（2026-08-05 latex 血泪）: 排版引擎不支持可变字体，必须用静态 TTF。
# google/fonts 仓库已全面转向可变字体（static/ 目录 404），故用 fonttools
# varLib.instancer 把官方可变字体实例化为标准静态 TTF。
#
# presswire 字体清单（含 CJK，presswire N1 依赖）:
#   Noto Sans SC   —— 中文黑体（正文）
#   Noto Serif SC  —— 中文宋体（标题 / 正文备选）
#   Noto Sans      —— 拉丁无衬线
#   Noto Serif     —— 拉丁衬线
#
# 幂等: 目标静态 TTF 已存在则跳过下载与实例化。
# 已知限制: Noto Sans SC / Noto Serif SC 可变字体较大（≈18MB / 25MB），
# 首次下载 + 实例化较慢（数分钟级）。
set -euo pipefail

# 探测全局 fonts 目录: 优先用户级 ~/.local/share/fonts（无需 sudo），
# 系统级 /usr/share/fonts 仅在可写时使用（如 CI root 容器）。
if [[ -w "$HOME/.local/share/fonts" ]]; then
  FONTS_DIR="$HOME/.local/share/fonts"
elif [[ -w "/usr/share/fonts" ]]; then
  FONTS_DIR="/usr/share/fonts"
else
  FONTS_DIR="$HOME/.local/share/fonts"
fi
mkdir -p "$FONTS_DIR"

# fonttools 兼容多种 pip 环境（CI runner / PEP 668 管理的系统 Python）
if ! python3 -c "import fontTools" 2>/dev/null; then
  python3 -m pip install --quiet --break-system-packages fonttools 2>/dev/null \
    || python3 -m pip install --quiet --user fonttools 2>/dev/null \
    || pip install --quiet fonttools
fi

GH="https://github.com/google/fonts/raw/main"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# static: 下载可变字体并实例化为静态 TTF（目标已存在则跳过 —— 幂等）
# $1=远端路径  $2=本地缓存名  $3=instancer 参数  $4=输出文件名
static() {
  local out="$FONTS_DIR/$4"
  if [[ -f "$out" ]]; then
    echo "skip  $4 (已存在)"
    return 0
  fi
  [[ -f "$TMP/$2" ]] || curl -fsSL -o "$TMP/$2" "$GH/$1"
  echo "生成 $4 ..."
  python3 -m fontTools.varLib.instancer "$TMP/$2" $3 -o "$out" > /dev/null 2>&1
}

# --- 中文: Noto Sans SC（黑体，正文）---
static "ofl/notosanssc/NotoSansSC%5Bwght%5D.ttf" "notosanssc.ttf" "wght=400" "NotoSansSC-Regular.ttf"
static "ofl/notosanssc/NotoSansSC%5Bwght%5D.ttf" "notosanssc.ttf" "wght=700" "NotoSansSC-Bold.ttf"

# --- 中文: Noto Serif SC（宋体，标题 / 正文备选）---
static "ofl/notoserifsc/NotoSerifSC%5Bwght%5D.ttf" "notoserifsc.ttf" "wght=400" "NotoSerifSC-Regular.ttf"
static "ofl/notoserifsc/NotoSerifSC%5Bwght%5D.ttf" "notoserifsc.ttf" "wght=700" "NotoSerifSC-Bold.ttf"

# --- 拉丁无衬线: Noto Sans ---
static "ofl/notosans/NotoSans%5Bwdth%2Cwght%5D.ttf" "notosans.ttf" "wdth=100 wght=400" "NotoSans-Regular.ttf"
static "ofl/notosans/NotoSans%5Bwdth%2Cwght%5D.ttf" "notosans.ttf" "wdth=100 wght=700" "NotoSans-Bold.ttf"

# --- 拉丁衬线: Noto Serif ---
static "ofl/notoserif/NotoSerif%5Bwdth%2Cwght%5D.ttf" "notoserif.ttf" "wdth=100 wght=400" "NotoSerif-Regular.ttf"
static "ofl/notoserif/NotoSerif%5Bwdth%2Cwght%5D.ttf" "notoserif.ttf" "wdth=100 wght=700" "NotoSerif-Bold.ttf"

fc-cache -f "$FONTS_DIR" > /dev/null 2>&1
echo "--- 已注册字体 ---"
fc-list | grep -iE "Noto Sans SC:|Noto Serif SC:|Noto Sans:|Noto Serif:" \
  || { echo "❌ 字体注册失败"; exit 1; }
