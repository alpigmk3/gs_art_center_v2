# -*- coding: utf-8 -*-
import codecs

def extract():
    src_path = r"c:\WORK\gs_art_center_v2\index_smaple02.html"
    dest_path = r"c:\WORK\gs_art_center_v2\seatmap_layout.html"
    
    print("Reading index_smaple02.html...")
    with codecs.open(src_path, "r", "utf-8") as f:
        lines = f.readlines()
    
    # Lines are 1-indexed. We want 639 to 2730 inclusive.
    # Python indices: 638 to 2730
    extracted_lines = lines[638:2730]
    
    print(f"Writing {len(extracted_lines)} lines to seatmap_layout.html...")
    with codecs.open(dest_path, "w", "utf-8") as f:
        f.writelines(extracted_lines)
    
    print("Extraction completed successfully!")

if __name__ == "__main__":
    extract()
