"""
Fill SVG seat IDs by matching rect positions to the JS seat map data.
"""

import re
import json
import sys
import os

# Use absolute paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
JS_FILE = os.path.join(SCRIPT_DIR, 'gs_arts_center_seatmap.js')
SVG_FILE = os.path.join(SCRIPT_DIR, 'seatmap_kor.svg')
OUTPUT_FILE = os.path.join(SCRIPT_DIR, 'seatmap_kor.svg')

def parse_js_seat_data(js_file):
    """Parse the JS file to extract seat data with View_IDs."""
    with open(js_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace NaN with null for JSON parsing
    content = content.replace('NaN', 'null')
    
    # Extract the array
    match = re.search(r'GS_ARTS_CENTER_SEAT_MAP_DATA\s*=\s*(\[.*?\]);', content, re.DOTALL)
    if not match:
        print("ERROR: Could not find GS_ARTS_CENTER_SEAT_MAP_DATA in JS file")
        sys.exit(1)
    
    data = json.loads(match.group(1))
    return data

def parse_svg_rects(svg_file):
    """Parse SVG file to find all rect elements (13x15 seat rects)."""
    with open(svg_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all rect elements that are seats (width=13, height=15)
    # They may or may not have an id attribute
    rect_pattern = re.compile(
        r'<rect\s+'
        r'(?:id="([^"]*?)"\s+)?'  # optional id
        r'x="([^"]*?)"\s+'
        r'y="([^"]*?)"\s+'
        r'width="13"\s+'
        r'height="15"\s+'
        r'transform="rotate\(([^)]*)\)"\s+'
        r'stroke="black"\s*/>'
    )
    
    rects = []
    for m in rect_pattern.finditer(content):
        rect_id = m.group(1)  # may be None
        x = float(m.group(2))
        y = float(m.group(3))
        transform = m.group(4)
        rotation = float(transform.split()[0])
        
        rects.append({
            'id': rect_id,
            'x': x,
            'y': y,
            'rotation': rotation,
            'match_start': m.start(),
            'match_end': m.end(),
            'full_match': m.group(0)
        })
    
    return rects, content

def main():
    print(f"JS file: {JS_FILE}")
    print(f"SVG file: {SVG_FILE}")
    
    # Parse JS data
    seat_data = parse_js_seat_data(JS_FILE)
    print(f"Parsed {len(seat_data)} seats from JS data")
    
    # Parse SVG
    rects, svg_content = parse_svg_rects(SVG_FILE)
    print(f"Parsed {len(rects)} seat rect elements from SVG")
    
    # Analyze rotation groups
    rot_groups = {}
    for r in rects:
        rot = r['rotation']
        if rot not in rot_groups:
            rot_groups[rot] = []
        rot_groups[rot].append(r)
    
    for rot in sorted(rot_groups.keys()):
        items = rot_groups[rot]
        with_id = sum(1 for r in items if r['id'])
        without_id = sum(1 for r in items if not r['id'])
        print(f"  Rotation {rot}: {len(items)} rects ({with_id} with ID, {without_id} without ID)")
        # Show sample existing IDs
        existing = [r['id'] for r in items if r['id']]
        if existing:
            print(f"    Sample IDs: {existing[:5]}...{existing[-3:]}")
    
    # Determine zone mapping from existing IDs
    rot_zones = {}
    for rot, items in rot_groups.items():
        zones = set()
        for r in items:
            if r['id']:
                parts = r['id'].split('_')
                if len(parts) >= 3:
                    floor_zone = f"{parts[1]}_{parts[2]}"
                    zones.add(floor_zone)
        rot_zones[rot] = zones
    
    print(f"\nRotation -> Zone mapping:")
    for rot, zones in sorted(rot_zones.items()):
        print(f"  {rot}: {sorted(zones)}")
    
    # Group JS data by Floor_Zone
    js_by_zone = {}
    for item in seat_data:
        key = f"{item['Floor']}_{item['Zone']}"
        if key not in js_by_zone:
            js_by_zone[key] = []
        js_by_zone[key].append(item)
    
    print(f"\nJS data zones:")
    for key in sorted(js_by_zone.keys()):
        print(f"  {key}: {len(js_by_zone[key])} seats")
    
    # Build the ordered View_ID list for each rotation group
    # We need to figure out the order of zones within each rotation group
    for rot, items in sorted(rot_groups.items()):
        zones = rot_zones.get(rot, set())
        if not zones:
            print(f"\nWARNING: Rotation {rot} has no identified zones")
            continue
        
        # Determine zone order by looking at the rect positions
        # The first rects with IDs tell us the order
        zone_order = []
        seen_zones = set()
        for r in items:
            if r['id']:
                parts = r['id'].split('_')
                if len(parts) >= 3:
                    fz = f"{parts[1]}_{parts[2]}"
                    if fz not in seen_zones:
                        zone_order.append(fz)
                        seen_zones.add(fz)
        
        # Add any zones from the rotation group that weren't in existing IDs
        # (shouldn't happen but just in case)
        for z in sorted(zones - seen_zones):
            zone_order.append(z)
        
        print(f"\nRotation {rot} zone order: {zone_order}")
        
        # Build complete ordered View_ID list
        ordered_view_ids = []
        for fz in zone_order:
            if fz in js_by_zone:
                for item in js_by_zone[fz]:
                    ordered_view_ids.append(item['View_ID'])
        
        print(f"  Expected {len(ordered_view_ids)} View_IDs, have {len(items)} rects")
        
        if len(items) != len(ordered_view_ids):
            print(f"  WARNING: Count mismatch!")
            # Let's see what's going on
            continue
        
        # Match rects to View_IDs
        mismatches = 0
        fills = 0
        for i, rect in enumerate(items):
            expected_id = ordered_view_ids[i]
            if rect['id']:
                if rect['id'] != expected_id:
                    mismatches += 1
                    if mismatches <= 10:
                        print(f"  MISMATCH [{i}]: SVG='{rect['id']}' expected='{expected_id}'")
            else:
                rect['new_id'] = expected_id
                fills += 1
        
        print(f"  Verified: {mismatches} mismatches, {fills} IDs to fill")
    
    # Apply changes
    changes = [(r['match_start'], r['match_end'], r['full_match'], r['new_id']) 
               for r in rects if 'new_id' in r]
    
    print(f"\n{'='*60}")
    print(f"Total IDs to fill: {len(changes)}")
    
    if not changes:
        print("No changes needed!")
        return
    
    # Show first few changes
    for start, end, old_text, new_id in changes[:5]:
        print(f"  + {new_id}")
    if len(changes) > 5:
        print(f"  ... and {len(changes) - 5} more")
    
    # Sort by position (reverse) to make replacements from end to start
    changes.sort(key=lambda c: c[0], reverse=True)
    
    new_svg = svg_content
    for start, end, old_text, new_id in changes:
        new_text = old_text.replace('<rect ', f'<rect id="{new_id}" ', 1)
        new_svg = new_svg[:start] + new_text + new_svg[end:]
    
    # Write output
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(new_svg)
    
    print(f"\nDone! Written updated SVG to {OUTPUT_FILE}")
    print(f"Added {len(changes)} seat IDs")

if __name__ == '__main__':
    main()
