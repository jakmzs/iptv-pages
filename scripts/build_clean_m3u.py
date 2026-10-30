#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
构建「干净全量」中文直播源：全部 CCTV + 全部省级卫视 + 大量地方台。

源：iptv-org 中国提交池（orgcn 镜像，已确认无成人台、IPv4 可播）。
策略：
  - 只保留中文频道（orgcn 本身即中国分类，再剔除成人关键字命中）
  - 按名称归组：央视频道 / 卫视频道 / 地方台
  - 同名频道多分辨率去重，保留画质最佳的一条
输出：site/result.m3u（标准 #EXTM3U，播放器直接可用）
"""
import os
import re
import urllib.request

OUTDIR = "site"
TARGET = os.path.join(OUTDIR, "result.m3u")

SOURCES = [
    ("orgcn(iptv-org CN 镜像)", "https://orgcn.jakmz.de5.net/"),
    ("iptv-org CN 官方兜底", "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/cn.m3u"),
]

ADULT = re.compile(r"(成人|福利|激情|性感|色情|裸|私房|午夜|伦理|porn|adult|xxx|sex)", re.I)

TAG_RE = re.compile(
    r"\s*[\(\[](?:1080p|1080P|720p|720P|576p|576i|540p|480p|360p|SD|HD|4K|8K|"
    r"Geo-blocked|Not 24/7)[\]\)]",
    re.I,
)

QUAL_RANK = {
    "1080p": 5, "1080P": 5, "4K": 5, "8K": 5,
    "720p": 4, "720P": 4, "HD": 3, "576p": 3, "576i": 3,
    "540p": 2, "480p": 2, "360p": 1, "SD": 0,
}


def fetch(url, timeout=120):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "ignore")


def norm_key(name):
    return TAG_RE.sub("", name).strip()


def group_of(name):
    if re.search(r"CCTV|CETV|央视|中央|中国中央电视台", name, re.I):
        return "央视频道"
    if "卫视" in name:
        return "卫视频道"
    return "地方台"


def quality_score(name):
    s = 0
    for q, r in QUAL_RANK.items():
        if q in name:
            s = max(s, r)
    if "Geo-blocked" in name or "Not 24/7" in name:
        s -= 1
    return s


def parse(data):
    entries = []
    lines = data.splitlines()
    for i, ln in enumerate(lines):
        if not ln.startswith("#EXTINF"):
            continue
        url = lines[i + 1].strip() if i + 1 < len(lines) else ""
        if not url or not url.startswith("http"):
            continue
        name = ln.split(",", 1)[1].strip() if "," in ln else ""
        if ADULT.search(ln):
            continue
        entries.append((name, url, group_of(name)))
    return entries


def main():
    all_entries = []
    for tag, url in SOURCES:
        try:
            ents = parse(fetch(url))
        except Exception as e:  # noqa: BLE001
            print("fetch err", tag, e)
            continue
        print(f"{tag}: parsed {len(ents)}")
        all_entries += ents

    # 同名（去画质标签后）去重，保留画质最佳
    best = {}
    for name, url, grp in all_entries:
        key = norm_key(name) or name
        score = quality_score(name)
        cur = best.get(key)
        if cur is None or score > cur[3] or (score == cur[3] and len(name) < len(cur[0])):
            best[key] = (name, url, grp, score)

    groups = {"央视频道": [], "卫视频道": [], "地方台": []}
    for _key, (name, url, grp, _s) in best.items():
        groups.setdefault(grp, []).append((name, url))

    out = ["#EXTM3U"]
    for g in ["央视频道", "卫视频道", "地方台"]:
        for name, url in groups.get(g, []):
            out.append(f'#EXTINF:-1 group-title="{g}",{name}')
            out.append(url)

    os.makedirs(OUTDIR, exist_ok=True)
    with open(TARGET, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")

    print(
        f"result.m3u 生成：共 {len(best)} 个频道 | "
        f"央视 {len(groups['央视频道'])} | 卫视 {len(groups['卫视频道'])} | "
        f"地方台 {len(groups['地方台'])} | 字节 {os.path.getsize(TARGET)}"
    )


if __name__ == "__main__":
    main()
