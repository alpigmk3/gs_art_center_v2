# -*- coding: utf-8 -*-
"""
inject_svg_ids.py  ── 좌표 기반 SVG 좌석 ID 주입기 (전체 구역 버전)
=======================================================================
SVG 의 <rect> 요소를 좌표(x, y) 및 회전 방향으로 구역을 구분하여
Floor / Zone / Row / Seat 순서로 매핑한 뒤
GS_ARTS_CENTER_SEAT_MAP_DATA 의 View_ID 를 id 속성으로 주입합니다.

SVG 구역 레이아웃 (백업 파일 분석 결과):
  ┌──────────────────────────────────────────────────────┐
  │  1F B (y=110~205, x=140~240, rotate+7)               │
  │  1F A (y=200~610, x=80~235,  rotate+7)               │
  │  1F C (y=110~205, x=450~560, rotate-7)               │
  ├──────────────────────────────────────────────────────┤
  │  2F A (y=610~950, x=80~240,  rotate+7)               │
  │  2F B (y=610~700, x=140~400, rotate+7)               │
  │  2F C (y=610~700, x=450~620, rotate-7)               │
  ├──────────────────────────────────────────────────────┤
  │  3F A (y=950~1232, x=80~300, rotate+7)               │
  │  3F B (y=950~1070, x=140~420,rotate+7)               │
  │  3F C (y=950~1070, x=430~620,rotate-7)               │
  └──────────────────────────────────────────────────────┘

  ※ B/C 구역 경계와 2F/3F 경계는 실행 시 진단 출력으로 조정 가능
"""

import json
import re
import os

# ───────────────────────────────────────────────────────────────
#  SECTIONS : 처리할 구역 목록
#  (Floor, Zone,  y_min, y_max,  x_min, x_max,  x_sort_asc)
#  x_sort_asc=True  → x 오름차순 (좌→우 = 작은번호→큰번호)
#  x_sort_asc=False → x 내림차순 (우→좌 = 작은번호→큰번호)
# ───────────────────────────────────────────────────────────────
SECTIONS = [
    # 1층
    ('1F', 'A',   200,  615,   80, 240, True),
    ('1F', 'B',   108,  210,  140, 370, True),
    ('1F', 'C',   108,  210,  450, 580, False),   # rotate(-7): x 내림차순
    # 2층
    ('2F', 'A',   615,  950,   80, 260, True),
    ('2F', 'B',   615,  730,  250, 440, True),
    ('2F', 'C',   615,  730,  430, 620, False),
    # 3층
    ('3F', 'A',   950, 1232,   80, 320, True),
    ('3F', 'B',   950, 1100,  300, 460, True),
    ('3F', 'C',   950, 1100,  440, 640, False),
]

# 행(Row) 클러스터를 나누는 y 간격 임계값 (픽셀)
ROW_GAP_THRESHOLD = 4.0

# 동일 위치 중복 rect 를 판단하는 거리 임계값 (픽셀)
DUPLICATE_XY_THRESHOLD = 0.5


def load_js_seat_data(js_path: str):
    print(f"📖 JS 파일 읽는 중: {js_path}")
    with open(js_path, "r", encoding="utf-8") as f:
        js_content = f.read()

    idx = js_content.find("GS_ARTS_CENTER_SEAT_MAP_DATA")
    if idx == -1:
        raise ValueError("❌ GS_ARTS_CENTER_SEAT_MAP_DATA 를 찾을 수 없습니다.")
    sb = js_content.find("[", idx)
    eb = js_content.rfind("]")
    raw = js_content[sb: eb + 1].replace("NaN", "null")
    data = json.loads(raw)
    print(f"   총 좌석 수: {len(data)}")
    return data


def parse_svg_seat_rects(svg_content: str):
    """
    SVG 에서 좌석 크기의 <rect> 요소를 모두 추출한다.
    동일한 (x, y) 위치에 중복 rect 가 있는 경우(fill + stroke 쌍)
    첫 번째 것만 대표로 보관하고 나머지를 duplicates 에 기록한다.
    """
    rect_pat = re.compile(r"<rect\s+([^>]*?)(/)?>", re.DOTALL)
    unique_pos = {}   # (round_x, round_y) → first rect info
    all_rects  = []   # 모든 rect (중복 포함), start → info

    for m in rect_pat.finditer(svg_content):
        attrs = m.group(1)
        x_m = re.search(r'\bx="([^"]+)"', attrs)
        y_m = re.search(r'\by="([^"]+)"', attrs)
        w_m = re.search(r'\bwidth="([^"]+)"', attrs)
        h_m = re.search(r'\bheight="([^"]+)"', attrs)
        if not (x_m and y_m and w_m and h_m):
            continue
        try:
            x = float(x_m.group(1))
            y = float(y_m.group(1))
            w = float(w_m.group(1))
            h = float(h_m.group(1))
        except ValueError:
            continue
        if not (5 <= w <= 50 and 5 <= h <= 50):
            continue

        key = (round(x, 1), round(y, 1))
        info = {
            'x': x, 'y': y, 'w': w, 'h': h,
            'start': m.start(), 'end': m.end(),
            'attrs': attrs,
            'selfclose': m.group(2) or '',
            'is_primary': key not in unique_pos,   # 중복 여부
        }
        all_rects.append(info)
        if key not in unique_pos:
            unique_pos[key] = info

    print(f"   SVG rect 총수: {len(all_rects)}, 고유 위치 수: {len(unique_pos)}")
    return all_rects, unique_pos


def cluster_rows(rects, gap_threshold=ROW_GAP_THRESHOLD):
    """y 값을 기준으로 정렬 후 gap_threshold 초과 시 새 행 클러스터 생성."""
    sorted_rects = sorted(rects, key=lambda r: (r['y'], r['x']))
    rows = []
    cur  = []
    prev_y = None
    for r in sorted_rects:
        if prev_y is None or (r['y'] - prev_y) > gap_threshold:
            if cur:
                rows.append(cur)
            cur = [r]
        else:
            cur.append(r)
        prev_y = r['y']
    if cur:
        rows.append(cur)
    return rows


def build_js_rows(all_seats, floor, zone):
    """특정 Floor/Zone 의 JS 좌석 데이터를 행별로 그룹화 (none 타입 제외)."""
    js_rows = {}
    for s in all_seats:
        if s.get('Floor') != floor or s.get('Zone') != zone:
            continue
        if s.get('Seat_Type') == 'none':
            continue
        row = s['Row']
        js_rows.setdefault(row, []).append(s)

    row_names = sorted(js_rows.keys(), key=lambda r: int(r.replace('열', '')))
    for rn in row_names:
        js_rows[rn].sort(key=lambda s: s['Seat_Number'])
    return row_names, js_rows


def inject():
    base    = r"c:\WORK\gs_art_center_v2"
    js_path = os.path.join(base, "gs_arts_center_seatmap.js")
    svg_src = os.path.join(base, "seatmap_kor - 복사본 (2).svg")   # 원본 백업 SVG
    svg_out = os.path.join(base, "seatmap_kor.svg")                  # 출력 파일

    # ── 1. 데이터 로드 ────────────────────────────────────────────
    all_seats = load_js_seat_data(js_path)
    print(f"📖 SVG 읽는 중: {svg_src}")
    with open(svg_src, "r", encoding="utf-8") as f:
        svg_content = f.read()

    # ── 2. SVG rect 파싱 (중복 위치 탐지 포함) ────────────────────
    all_rects, unique_pos = parse_svg_seat_rects(svg_content)

    # ── 3. 섹션별 ID 매핑 ─────────────────────────────────────────
    #   primary_id_map : 고유 위치의 첫 rect start → view_id
    primary_id_map = {}   # start_pos → view_id
    # 중복 rect (같은 위치에 여러 rect) 도 동일 view_id 부여
    pos_to_id = {}        # (round_x, round_y) → view_id

    total_ok = 0
    total_warn = 0

    for (floor, zone, y_min, y_max, x_min, x_max, x_sort_asc) in SECTIONS:
        print(f"\n{'='*58}")
        print(f"  처리 중: {floor} Zone {zone}  "
              f"[x:{x_min}-{x_max}, y:{y_min}-{y_max}]")
        print(f"{'='*58}")

        # 고유 위치 rect 중 이 구역에 속하는 것만
        section_uniq = [
            r for r in unique_pos.values()
            if y_min <= r['y'] < y_max and x_min <= r['x'] < x_max
        ]
        print(f"  고유 좌석 위치 수: {len(section_uniq)}")

        if not section_uniq:
            print("  ⚠️  이 구역에서 rect 를 찾지 못했습니다. 좌표 범위를 확인하세요.")
            continue

        # SVG 행 클러스터링
        svg_rows = cluster_rows(section_uniq)
        print(f"  SVG 행 클러스터 수: {len(svg_rows)}")

        # JS 행 데이터
        row_names, js_rows = build_js_rows(all_seats, floor, zone)
        print(f"  JS 활성 행 수     : {len(row_names)}")

        # 진단 출력
        print()
        for ri, svg_row in enumerate(svg_rows):
            xs = [r['x'] for r in svg_row]
            ys = [r['y'] for r in svg_row]
            if ri < len(row_names):
                rn = row_names[ri]
                js_cnt = len(js_rows[rn])
                ok = "✅" if len(svg_row) == js_cnt else "⚠️"
                if ok == "✅":
                    total_ok += 1
                else:
                    total_warn += 1
                print(f"  {ok} SVG행{ri+1:2d} ({len(svg_row):2d}개) "
                      f"y=[{min(ys):.1f}~{max(ys):.1f}] "
                      f"x=[{min(xs):.1f}~{max(xs):.1f}] "
                      f"← JS {rn} ({js_cnt}석)")
            else:
                total_warn += 1
                print(f"  ⛔ SVG행{ri+1:2d} ({len(svg_row):2d}개) "
                      f"y=[{min(ys):.1f}~{max(ys):.1f}] ← JS 행 없음!")

        # 행-좌석 매핑
        matched = 0
        for ri, row_name in enumerate(row_names):
            if ri >= len(svg_rows):
                print(f"  ⛔ JS {row_name}: 매칭할 SVG 행 없음!")
                continue

            # x 방향 정렬: Zone A/B = 오름차순, Zone C = 내림차순
            svg_row = sorted(svg_rows[ri], key=lambda r: r['x'],
                             reverse=not x_sort_asc)
            js_seats = js_rows[row_name]

            pair_count = min(len(svg_row), len(js_seats))
            for si in range(pair_count):
                key = (round(svg_row[si]['x'], 1), round(svg_row[si]['y'], 1))
                pos_to_id[key] = js_seats[si]['View_ID']
                matched += 1

            if len(svg_row) != len(js_seats):
                print(f"  ⚠️  {row_name}: SVG {len(svg_row)}개 ≠ JS {len(js_seats)}석 "
                      f"→ {pair_count}개 매핑")

        print(f"\n  이 구역 매핑 완료: {matched}개")

    print(f"\n{'='*58}")
    print(f"📝 전체 매핑 위치 수: {len(pos_to_id)}")
    print(f"   ✅ 완전 일치 행: {total_ok}")
    print(f"   ⚠️  불일치 행:   {total_warn}")

    # ── 4. 모든 rect 에 대해 pos 기반으로 id_map 구성 ─────────────
    #   (중복 rect 도 동일 view_id 부여)
    id_map = {}
    for r in all_rects:
        key = (round(r['x'], 1), round(r['y'], 1))
        if key in pos_to_id:
            id_map[r['start']] = pos_to_id[key]

    print(f"   id 주입 대상 rect (중복 포함): {len(id_map)}")

    # ── 5. SVG 문자열 재작성 ─────────────────────────────────────
    rect_pat = re.compile(r"<rect\s+([^>]*?)(/)?>", re.DOTALL)
    parts = []
    last  = 0

    for m in rect_pat.finditer(svg_content):
        if m.start() not in id_map:
            continue
        view_id  = id_map[m.start()]
        attrs    = m.group(1)
        sc       = m.group(2) or ''

        if 'id="' in attrs:
            new_attrs = re.sub(r'id="[^"]*"', f'id="{view_id}"', attrs)
        else:
            new_attrs = f'id="{view_id}" ' + attrs

        parts.append(svg_content[last: m.start()])
        parts.append(f'<rect {new_attrs}{sc}>')
        last = m.end()

    parts.append(svg_content[last:])
    final_svg = "".join(parts)

    # ── 6. 파일 저장 ─────────────────────────────────────────────
    with open(svg_out, "w", encoding="utf-8") as f:
        f.write(final_svg)

    print(f"\n✅ 완료! → {svg_out}")
    print(f"   ID 주입 rect : {len(id_map)}")
    print(f"   ID 미주입 rect: {len(all_rects) - len(id_map)}")


if __name__ == "__main__":
    inject()
