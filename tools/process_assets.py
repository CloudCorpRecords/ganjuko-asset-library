#!/usr/bin/env python3
"""Trim raw 1024px generations and fit them into footprint cell boxes.

Usage: process_assets.py --base WORKDIR
WORKDIR contains raw*/ dirs (generations) and receives out_assets/<group>/.
Raw lookup per group comes from meta.RAW_DIRS. Processing: crush alpha < 8,
crop to alpha bbox, zero hidden RGB, scale-to-fit preserving aspect,
bottom-anchor into the footprint box (feet on the bottom edge).
Runs identically on the VM and on the Mac.
"""
import argparse, os, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import meta

CELL = 48

def find_raw(base, group, slug):
    for d in meta.RAW_DIRS[group]:
        p = os.path.join(base, d, slug + ".png")
        if os.path.exists(p) and os.path.getsize(p) > 10000:
            return p
    return None

def process(src, dst, w, h):
    im = Image.open(src).convert("RGBA")
    a = im.getchannel("A").point(lambda v: 0 if v < 8 else v)
    bbox = a.getbbox()
    if not bbox:
        raise RuntimeError("fully transparent")
    im.putalpha(a)
    black = Image.new("RGBA", im.size, (0, 0, 0, 0))
    mask = a.point(lambda v: 255 if v > 0 else 0)
    im = Image.composite(im, black, mask).crop(bbox)
    bw, bh = w * CELL, h * CELL
    scale = min(bw / im.width, bh / im.height)
    nw, nh = max(1, round(im.width * scale)), max(1, round(im.height * scale))
    im = im.resize((nw, nh), Image.LANCZOS)
    out = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    out.paste(im, ((bw - nw) // 2, bh - nh), im)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    out.save(dst)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    a = ap.parse_args()
    groups = {"commons": meta.COMMONS}
    for kit, info in meta.KITS.items():
        groups[kit] = info["assets"]
    ok, bad = 0, []
    for group, assets in groups.items():
        for aid, _n, _c, _s, (w, h), _l, _b, _d in assets:
            src = find_raw(a.base, group, aid)
            dst = os.path.join(a.base, "out_assets", group, aid + ".png")
            if not src:
                bad.append((aid, "no raw"))
                continue
            try:
                process(src, dst, w, h)
                ok += 1
            except Exception as e:
                bad.append((aid, str(e)))
    print("processed:", ok)
    for aid, why in bad:
        print("FAILED:", aid, "-", why)

if __name__ == "__main__":
    main()
