#!/usr/bin/env python3
"""Ganjuko Asset Library assembler (data-driven, multi-kit).

Usage: assembler.py --base WORKDIR --out OUTDIR [--status STATUS.json ...]
WORKDIR contains out_assets/<group>/ (from process_assets.py).
For every kit, builds a COMBINED sheet = commons assets + the kit's assets,
and emits per-kit sheet PNG, sheetmap-<kit>.json, tileset-fragment-<kit>.json,
plus the global library.json catalog (with a "biome" field per asset).

RMMZ flag bits (confirmed in razer-original js/rmmz_objects.js Game_Map and
js/rmmz_core.js Tilemap):
  0x01/0x02/0x04/0x08  block passage DOWN/LEFT/RIGHT/UP (bit set = impassable)
  0x10 star (above player, no passage effect)  0x20 ladder   0x40 bush
  0x80 counter   0x100 damage floor   0x200 boat   0x400 ship   0x800 airship
  bits 12+ (flag >> 12) = terrain tag.  B-sheet tile ids start at 2048.
"""
import argparse, json, os, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import meta

CELL = 48
SHEET_COLS = 16
TILE_ID_B = 2048
FLAGS_LEN = 8192

CELL_FLAGS = {
    "block":   0x0F,
    "pass":    0x00,
    "star":    0x10,
    "counter": 0x0F | 0x80,
    "bush":    0x40,
}

def passage_summary(layout):
    vals = {CELL_FLAGS[c] for r in layout for c in r}
    if vals == {0x0F}:
        return "block"
    if vals == {0x00}:
        return "pass"
    if vals == {0x10}:
        return "star"
    return "mixed"

def record(aid, name, cat, sub, w, h, layout, blurb, biome, gen):
    item = gen.get(aid, {}) if isinstance(gen.get(aid), dict) else {}
    return {
        "id": aid, "name": name, "category": cat, "theme": sub, "biome": biome,
        "blurb": blurb,
        "footprint": {"w": w, "h": h}, "anchor": "bottom",
        "attributes": {
            "passage": passage_summary(layout),
            "counter": any(CELL_FLAGS[c] & 0x80 for r in layout for c in r),
            "bush": any(CELL_FLAGS[c] & 0x40 for r in layout for c in r),
            "ladder": False, "damageFloor": False, "terrainTag": 0,
        },
        "cellLayout": layout,
        "style": "ganjuko-pixel-v1",
        "prompt": item.get("prompt", ""),
        "model": item.get("model", ""),
        "generated": "2026-11-01",
        "license": "Original generated art, (c) Rene Turcios",
    }

def pack(records):
    order = sorted(records, key=lambda r: (-r["footprint"]["h"], -r["footprint"]["w"], r["id"]))
    shelves, placements = [], {}
    for r in order:
        w, h = r["footprint"]["w"], r["footprint"]["h"]
        for s in shelves:
            if s[1] >= h and s[2] + w <= SHEET_COLS:
                placements[r["id"]] = (s[2], s[0])
                s[2] += w
                break
        else:
            y = sum(s[1] for s in shelves)
            assert y + h <= 16, "kit does not fit one 16x16 sheet"
            shelves.append([y, h, w])
            placements[r["id"]] = (0, y)
    return placements

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--status", nargs="*", default=[])
    a = ap.parse_args()
    gen = {}
    for sp in a.status:
        if os.path.exists(sp):
            gen.update(json.load(open(sp)).get("items", {}))

    def have(group, aid):
        return os.path.exists(os.path.join(a.base, "out_assets", group, aid + ".png"))

    catalog, missing = [], []
    biome_records = {}
    commons_records = []
    for aid, name, cat, sub, (w, h), layout, blurb, _d in meta.COMMONS:
        if have("commons", aid):
            r = record(aid, name, cat, sub, w, h, layout, blurb, "commons", gen)
            commons_records.append(r)
            catalog.append(r)
        else:
            missing.append(aid)
    for kit, info in meta.KITS.items():
        recs = []
        for aid, name, cat, sub, (w, h), layout, blurb, _d in info["assets"]:
            if have(kit, aid):
                r = record(aid, name, cat, sub, w, h, layout, blurb, kit, gen)
                recs.append(r)
                catalog.append(r)
            else:
                missing.append(aid)
        biome_records[kit] = recs
    if missing:
        print("MISSING (skipped):", ", ".join(sorted(set(missing))))

    for kit, info in meta.KITS.items():
        combined = commons_records + biome_records[kit]
        if not combined:
            continue
        placements = pack(combined)
        sheet = Image.new("RGBA", (768, 768), (0, 0, 0, 0))
        flags = [0] * FLAGS_LEN
        sheetmap = {}
        for r in combined:
            group = "commons" if r["biome"] == "commons" else kit
            cx, cy = placements[r["id"]]
            im = Image.open(os.path.join(a.base, "out_assets", group, r["id"] + ".png"))
            assert im.size == (r["footprint"]["w"] * CELL, r["footprint"]["h"] * CELL), r["id"]
            sheet.paste(im, (cx * CELL, cy * CELL), im)
            tile_ids = []
            for dy, rowcells in enumerate(r["cellLayout"]):
                for dx, code in enumerate(rowcells):
                    tid = TILE_ID_B + (cy + dy) * SHEET_COLS + (cx + dx)
                    flags[tid] = CELL_FLAGS[code] | (r["attributes"]["terrainTag"] << 12)
                    tile_ids.append(tid)
            sheetmap[r["id"]] = {"sheet": info["sheet"], "col": cx, "row": cy,
                                 "w": r["footprint"]["w"], "h": r["footprint"]["h"],
                                 "tileIds": tile_ids}
        kdir = os.path.join(a.out, "kits", kit)
        os.makedirs(os.path.join(kdir, "sheets"), exist_ok=True)
        sheet.save(os.path.join(kdir, "sheets", info["sheet"] + ".png"))
        fragment = {
            "id": None, "name": info["tilesetName"], "mode": 1,
            "tilesetNames": ["", "", "", "", "", info["sheet"], "", "", ""],
            "flags": flags,
            "note": ("Ganjuko Asset Library — " + info["tilesetName"] +
                     " (combined sheet: commons + " + kit + "). See library.json / sheetmap-" + kit + ".json."),
        }
        with open(os.path.join(kdir, "tileset-fragment-" + kit + ".json"), "w") as f:
            json.dump(fragment, f, indent=1)
        with open(os.path.join(kdir, "sheetmap-" + kit + ".json"), "w") as f:
            json.dump(sheetmap, f, indent=1)
        used = sum(1 for v in flags if v)
        print(f"{kit}: {len(combined)} assets on sheet ({len(biome_records[kit])} kit + {len(commons_records)} commons), {used} flag cells")

    with open(os.path.join(a.out, "library.json"), "w") as f:
        json.dump({"library": "ganjuko-asset-library", "version": 1,
                   "style": "ganjuko-pixel-v1", "tileSize": 48,
                   "assets": catalog}, f, indent=1)
    print("catalog records:", len(catalog))

if __name__ == "__main__":
    main()
