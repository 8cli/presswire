# 实验 N — CI 安装 typst 方案（任务 20 前置）

> 日期：2026-08-07 · 来源：gh 查 typst 官方 release + 社区 action 搜索

## 问题

任务 20（CI 迁移）需在 GitHub Actions 安装 typst CLI。linotype 用 texlive；presswire 换 typst。**官方推荐的安装方式？**

## 调研结果

### 方案 1：直接下载官方 release 二进制（最可靠，推荐）

**官方 release 资产格式**（gh 实证，v0.15.1）：
```
typst-x86_64-unknown-linux-musl.tar.xz
```

**Workflow 片段**（推荐，版本锁定 v0.15.1）：
```yaml
- name: Install typst
  run: |
    curl -L -o typst.tar.xz \
      https://github.com/typst/typst/releases/download/v0.15.1/typst-x86_64-unknown-linux-musl.tar.xz
    tar -xf typst.tar.xz
    sudo mv typst-x86_64-unknown-linux-musl/typst /usr/local/bin/typst
    typst --version
```

### 方案 2：社区 action

- `lvignoli/typst-action`（2026-08 更新，活跃）——封装下载+缓存。
- `Jarivanbakel/typst-action`（2023，较旧）。
- **不建议**依赖社区 action（版本 pinning 需 @vN 锁）；方案 1 直接 curl 最透明。

### 方案 3：apt/cargo（不推荐）

- apt 版旧；`cargo install typst` 编译慢（Rust 全量构建）。CI 用预编译二进制最快。

## 对 presswire 任务 20 的定案

```yaml
# CI: Ubuntu + Python 3.12 + typst CLI 0.15.1
- uses: actions/setup-python@v5
  with: { python-version: "3.12" }        # 3.14 无 typst wheel
- name: Install typst
  run: |
    curl -L -o typst.tar.xz https://github.com/typst/typst/releases/download/v0.15.1/typst-x86_64-unknown-linux-musl.tar.xz
    tar -xf typst.tar.xz && sudo mv typst-x86_64-unknown-linux-musl/typst /usr/local/bin/
- name: Install typst-py
  run: pip install typst==0.15.0
- name: Test
  run: |
    typst compile examples/...          # CLI 路径
    python3 tests/run_tests.py .        # 进程内 typst-py 路径
```

**版本锁定**：CLI v0.15.1 + typst-py 0.15.0 双锁（实测配套）。`typst compile` + `typst eval` 双命令都在 PATH 可用。

## 备注

- 若 CI 也要 font 安装 → `scripts/ci-install-fonts.sh`（任务 3 已备，Noto SC 静态字体）。
- Linux musl 静态二进制无 glibc 依赖，Ubuntu runner 直接跑。
- 升级 typst 时只改版本号一处（curl URL + pip 版本），CI 保持透明。
