# -*- coding: utf-8 -*-
"""
analyze_svg_zones.py
SVG 백업 파일에서 각 구역(Floor/Zone)의 좌표 범위를 자동 탐지합니다.
"""

import json
import re

JS_PATH   = r"c:\WORK\gs_art_center_v2\gs_arts_center_seatmap.js"
SVG_PATH  = r"c:\WORK\gs_art_center_v2\seatmap_kor - 복사본 (2).svg"

# ── JS 데이터 로드 ────────────────────────────────────────────
with open(JS_PATH, "r", encoding="utf-8") as f:
    c = f.read()
sb   = c.find('[', c.find('GS_ARTS_CENTER_SEAT_MAP_DATA'))
data = json.loads(c[sb : c.rfind(']') + 1].replace('NaN', 'null'))

from collections import defaultdict
zones = defaultdict(list)
for s in data:
    if s.get('Seat_Type') != 'none':
        zones[(s['Floor'], s['Zone'])].append(s)

print("=== JS 구역별 좌석 수 ===")
for k in sorted(zones.keys()):
    rows = sorted(set(s['Row'] for s in zones[k]), key=lambda r: int(r.replace('열','')))
    print(f"  {k[0]} Zone {k[1]}: {len(zones[k])}석, {len(rows)}행")

# ── SVG rect 파싱 ────────────────────────────────────────────
with open(SVG_PATH, "r", encoding="utf-8") as f:
    svg = f.read()

rect_pat = re.compile(r"<rect\s+([^>]*?)/?>")
rects = []
for m in rect_pat.finditer(svg):
    attrs = m.group(1)
    x_m = re.search(r'\bx="([^"]+)"', attrs)
    y_m = re.search(r'\by="([^"]+)"', attrs)
    w_m = re.search(r'\bwidth="([^"]+)"', attrs)
    h_m = re.search(r'\bheight="([^"]+)"', attrs)
    if not (x_m and y_m and w_m and h_m): continue
    try:
        x, y, w, h = float(x_m.group(1)), float(y_m.group(1)), float(w_m.group(1)), float(h_m.group(1))
    except ValueError:
        continue
    if 5 <= w <= 50 and 5 <= h <= 50:
        rects.append((x, y))

print(f"\n=== SVG 전체 rect 수: {len(rects)} ===")
print(f"  x 범위: {min(r[0] for r in rects):.1f} ~ {max(r[0] for r in rects):.1f}")
print(f"  y 범위: {min(r[1] for r in rects):.1f} ~ {max(r[1] for r in rects):.1f}")

# y 값을 구간으로 나눠서 분포 파악
print("\n=== y 좌표 분포 (100px 단위) ===")
buckets = defaultdict(int)
for x, y in rects:
    buckets[int(y // 100) * 100] += 1
for k in sorted(buckets.keys()):
    bar = '█' * (buckets[k] // 5)
    print(f"  y={k:4d}~{k+99}: {buckets[k]:4d}개  {bar}")

# x 값 분포
print("\n=== x 좌표 분포 (50px 단위) ===")
xbuckets = defaultdict(int)
for x, y in rects:
    xbuckets[int(x // 50) * 50] += 1
for k in sorted(xbuckets.keys()):
    bar = '█' * (xbuckets[k] // 5)
    print(f"  x={k:4d}~{k+49}: {xbuckets[k]:4d}개  {bar}")
