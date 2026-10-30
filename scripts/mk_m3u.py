#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iptv-api 结果兜底转 M3U：
1) 若引擎原生生成了 output/result.m3u（且像真 M3U），直接采用；
2) 否则把稳定产出的 output/result.txt 转换成标准 #EXTM3U。
自动跳过「更新时间」组的垃圾视频行，并按分组写入 group-title。
"""
import os

OUT = "output"
SITE = "site"
os.makedirs(SITE, exist_ok=True)

native = os.path.join(OUT, "result.m3u")
target = os.path.join(SITE, "result.m3u")
used_native = False

if os.path.exists(native) and os.path.getsize(native) > 0:
    data = open(native, encoding="utf-8", errors="ignore").read()
    if "#EXTM3U" in data or "#EXTINF" in data:
        with open(target, "w", encoding="utf-8") as f:
            f.write(data)
        used_native = True
        print("use native result.m3u")

if not used_native:
    txt = os.path.join(OUT, "result.txt")
    if os.path.exists(txt):
        lines = open(txt, encoding="utf-8", errors="ignore").read().splitlines()
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
        print(f"converted from result.txt, channels: {n}")
    else:
        print("no result.txt to convert")

if os.path.exists(target):
    print("result.m3u bytes:", os.path.getsize(target))
else:
    print("WARN: result.m3u not produced")
