#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 iptv-api 稳定产出的 output/result.txt 转换成标准 #EXTM3U 播放列表。

为什么不用容器原生 output/result.m3u？
  引擎在 Docker 容器内以 root 运行，产出的 result.m3u 常是 root 独有、
  宿主 runner 用户无读权限（实测 PermissionError）。而 result.txt 始终可读，
  因此统一以 result.txt 为准做转换，最稳。

自动跳过「更新时间」组里夹带的那条无关视频，并按分组写入 group-title。
"""
import os

OUT = "output"
SITE = "site"
os.makedirs(SITE, exist_ok=True)

target = os.path.join(SITE, "result.m3u")
txt = os.path.join(OUT, "result.txt")

if not os.path.exists(txt):
    print("WARN: result.txt 不存在，无法生成 M3U")
    raise SystemExit(0)

try:
    lines = open(txt, encoding="utf-8", errors="ignore").read().splitlines()
except Exception as e:
    print("WARN: 读取 result.txt 失败:", e)
    raise SystemExit(0)

cur = ""
out = ["#EXTM3U"]
for ln in lines:
    s = ln.strip()
    if not s:
        continue
    if ",#genre#" in s:
        g = s.split(",#genre#")[0].strip()
        # 「更新时间」组里夹带了一条无关视频，直接跳过该组
        cur = "" if g in ("🕘️更新时间", "更新时间") else g
        continue
    if "," in s:
        name, url = s.split(",", 1)
        name = name.strip()
        url = url.strip()
        if not name or not url:
            continue
        if cur == "" and ("kwimgs" in url or "update" in name.lower()):
            continue
        tvg = f' tvg-name="{name}"'
        if cur:
            tvg += f' group-title="{cur}"'
        out.append(f"#EXTINF:-1{tvg},{name}")
        out.append(url)

with open(target, "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")

n = sum(1 for l in out if l.startswith("#EXTINF"))
print(f"result.m3u 已生成，频道数: {n}，字节: {os.path.getsize(target)}")
