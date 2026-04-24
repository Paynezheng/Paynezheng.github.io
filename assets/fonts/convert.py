#!/usr/bin/env python3
"""
Convert Vulf Sans OTF files to WOFF2 for web use.
Run from the assets/fonts/ directory:
  python3.10 convert.py
"""
import os
from fontTools.ttLib import TTFont

INPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# Convert all OTF files in this directory
import glob
TARGET_FILES = [os.path.basename(p) for p in glob.glob(os.path.join(INPUT_DIR, "*.otf"))]

converted = 0
for filename in TARGET_FILES:
    src = os.path.join(INPUT_DIR, filename)
    if not os.path.exists(src):
        print(f"  SKIP (not found): {filename}")
        continue
    out_name = filename.replace(".otf", ".woff2")
    out_path = os.path.join(INPUT_DIR, out_name)
    try:
        font = TTFont(src)
        font.flavor = "woff2"
        font.save(out_path)
        size_kb = os.path.getsize(out_path) // 1024
        print(f"  OK  {out_name}  ({size_kb} KB)")
        converted += 1
    except Exception as e:
        print(f"  ERR {filename}: {e}")

print(f"\nDone: {converted} files converted.")
