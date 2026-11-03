# Ganjuko City Kit (Kits 1 + 2)

City-building pieces the stock RPG Maker Outside set doesn't have, in the
`ganjuko-pixel-v1` style. The combined sheet (`sheets/GanjukoCity_B.png`)
contains this kit **plus the shared commons** (trees, hedges, crates, rocks)
so a single B slot builds a whole town.

- **Sheet:** `sheets/GanjukoCity_B.png` (768x768, B slot)
- **Fragment:** `tileset-fragment-city.json` — paste into `data/Tilesets.json`,
  set `id` to the new index; all passage/star/counter/bush flags are encoded.
- **Layout map:** `sheetmap-city.json` (asset id -> cell + tile ids)
- **Catalog:** every asset is a record in `../../library.json` (`biome: "city"`
  or `"commons"`), with its exact generation prompt.

## Sub-themes

- **residential** — red/blue/pink-roof houses, green-roof cottage, brick
  townhouse, apartment block, balcony, window box, clothesline, garden
  fence, dog house, chimney.
- **commercial** — shop front, cafe, bakery, inn, wide storefront (front
  rows are **counters**: place an NPC behind the wall face and players can
  talk/trade across it), market stall, hanging sign, awning, menu board.
- **civic** — town hall, clock tower, fountain, hero statue, well, notice
  board, city gate arch and park gate (walk through the `pass` cell),
  flower arch.
- **street-props** — lamps (single/double), benches, mailbox, banner pole,
  signposts (all signage is **blank on purpose** — add lettering as events
  or in an image editor), hydrant, trash bin, bollards, bicycle rack,
  planters, flower beds (bush flag), manhole and puddle (flat, walkable).

Signs ship text-free by design: generated lettering is unreliable, and
blank boards let each game write its own names.
