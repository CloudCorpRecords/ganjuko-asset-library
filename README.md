# Ganjuko Asset Library

An open, multi-biome asset pack of original pixel-art tiles for 2D RPGs,
built for **Ganjuko** (an RPG Maker MZ monster-catcher) and designed to be
reused by any future game. Every tile is generated in one consistent style
(`ganjuko-pixel-v1`), trimmed, and — most importantly — shipped with its
**gameplay attributes already encoded** as RPG Maker tileset flags, so a
fountain blocks movement, a shop front works as a counter, and a canopy
hangs over the player's head, with zero manual flag-painting in the editor.

## What's inside

```
library.json            Global catalog: one record per asset (id, name,
                        category, biome, footprint, attributes, cell layout,
                        prompt, model, license).
commons/assets/         Shared assets reused by every biome (canonical trees,
                        rocks, grass tufts, crates...). Repetition here is
                        deliberate — it keeps biomes visually coherent.
kits/<biome>/           One kit per biome:
  assets/                 individual transparent PNGs (footprint x 48px)
  sheets/                 assembled B-style sheets (768x768, 48px grid):
                          commons + that biome, pre-packed for you
  tileset-fragment-<biome>.json
                          a ready-to-paste Tilesets.json entry whose flags
                          array already carries every tile's attributes
  sheetmap-<biome>.json   asset id -> sheet cell + RMMZ tile ids
  README.md               the kit's contents and notes
tools/                  meta.py (asset definitions), process_assets.py
                        (trim/fit raws), assembler.py (pack sheets + flags)
characters/assets/      NPC walk sheets (see the Characters section below)
```

## Use it in RPG Maker MZ (2 minutes)

1. Copy a kit's sheet PNG (e.g. `kits/city/sheets/GanjukoCity_B.png`) into
   your project's `img/tilesets/`.
2. Open your project's `data/Tilesets.json`, and append the object from
   `kits/city/tileset-fragment-city.json` as a new element of the array.
   Set its `"id"` to its new index in the array.
3. In the editor, create/select that tileset for your map and paint. The B
   sheet is fully flagged: passage, star (draw-above), counter, and bush
   behaviour come from the fragment — do not re-paint flags unless you want
   to override them.

**RPG Maker MV** uses the same 48px tiles and the same flag bits, so the
sheets and fragments work there too (paste the fragment the same way).

## Attribute encoding (RMMZ flags)

Each asset record carries a human-readable `attributes` block plus a
`cellLayout` grid (top row first). The assembler compiles cells to flag
words using the standard RPG Maker bits, verified against the MZ runtime
source (`Game_Map.checkPassage`, `Tilemap`):

| cell code | flag | meaning |
|---|---|---|
| `block` | `0x0F` | impassable in all four directions |
| `pass` | `0x00` | walkable in all directions |
| `star` | `0x10` | drawn above the player; no passage effect |
| `counter` | `0x8F` | impassable + counter (talk/trade across it) |
| `bush` | `0x40` | walkable + bush (feet hidden) |

Tall objects follow RPG Maker convention: the bottom row blocks (or acts as
a counter) and upper rows are `star`, so roofs and canopies draw over a
player walking behind them. Terrain tags live in bits 12+ of the flag word;
kit 1 uses tag 0 everywhere.

## Kits

- **City Kit 1 + 2** (`kits/city/`) — houses, shop fronts, town hall, clock
  tower, fountain, statue, market stalls, lamps, signage, street props.
- **Forest Kit 1** (`kits/forest/`) — tree clusters, canopy pieces, logs,
  stumps, mushrooms, ferns, a forest shrine, bridges, a campsite.
- **Mountain Kit 1** (`kits/mountain/`) — rock formations, snowy pines,
  shrine gate, rope bridge, mine entrance and props, hot spring.

Planned: Coast, Desert, Snow, Cave, Interiors.

## Characters (added 2026-11-01)

`characters/assets/` holds ready-to-use NPC walk sheets (`$NPC_*.png`,
RMMZ single-character format: 144x192, 3x4 frames of 48x48, rows
down/left/right/up). Drop one into a project's `img/characters/`, point any
event's image at it, done — no tileset entry needed.

How characters differ from tiles in this catalog: tiles are map geometry, so
their records carry RMMZ tile attributes (passage/star/counter flags,
footprint, cell layout). Characters are *event graphics*, so their
`library.json` records (kind: "character") carry role/theme/tags instead of
tile flags — an NPC's passability, movement and interaction live in the
event that uses the sheet, not in the art. The first set: Elder Storyteller,
Kid with Cap, Fisher, Hiker, Scientist, Shrine Keeper, Sailor, Miner,
Artist, Traveling Merchant.

## License

See LICENSE.md. Assets (all PNG art): **CC-BY 4.0** with credit to
**Rene Turcios**. Tools/code: **MIT**. The "Ganjuko" name is reserved by
the author — the licenses cover the files, not the brand.

## Provenance

All art is AI-generated (OpenAI `gpt-image-1-mini`, 2026-11-01) from text
prompts recorded in `library.json`, then programmatically fitted to exact
48px footprints. No stock RPG Maker (RTP) art is used or redistributed.
